"""Conferência e propostas de ajuste sem alterar as marcações."""
from datetime import date, datetime, time, timedelta
from uuid import UUID, uuid4

from flask import abort, g, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from app.admin import bp
from app.admin.auth import permission_required
from app.admin.onboarding import _open, _seal
from app.admin.reporting import _records, _scoped_users, _utc_midnight
from app.admin.dashboard import _local_time
from app.admin.simulation import simulated_ids
from app.attendance_reporting import summarize_punches
from app.models import Ponto, db
from app.observability import audit
from app.punch_review_models import PunchReview
from app.rbac import Permission


@bp.get("/ocorrencias")
@permission_required(Permission.PUNCH_VIEW)
def occurrences():
    start, end, users, employee_id, points = _records()
    daily = summarize_punches(points, start, end)
    marked = simulated_ids(points)
    ids = [u.id for u in users]
    if employee_id is not None:
        ids = [employee_id]
    events = (PunchReview.query.filter(PunchReview.user_id.in_(ids),
              PunchReview.day >= start, PunchReview.day <= end)
              .order_by(PunchReview.created_at.desc(), PunchReview.id.desc()).all())
    latest = {}
    for event in events:
        latest.setdefault((event.user_id,event.day), event)
    rows=[]
    for row in daily:
        if row["issues"] or row["occurrences"]:
            row["simulated"] = bool(marked.intersection(row["point_ids"]))
            row["review"] = latest.get((row["user_id"],row["day"]))
            rows.append(row)
    return render_template("admin/ocorrencias.html", rows=rows, users=users,
                           employee_id=employee_id, start=start, end=end)


def _scoped_subject(user_id, day_text):
    subject = _scoped_users().filter_by(id=user_id).first_or_404()
    try:
        day=date.fromisoformat(day_text)
    except ValueError:
        abort(400)
    return subject,day


def _day_context(subject, day):
    start=_utc_midnight(day)
    end=_utc_midnight(day+timedelta(days=1))
    points=(Ponto.query.filter(Ponto.user_id==subject.id, Ponto.timestamp>=start,
                              Ponto.timestamp<end).order_by(Ponto.timestamp, Ponto.id).all())
    rows=summarize_punches(points,day,day)
    events=(PunchReview.query.filter_by(user_id=subject.id,day=day)
            .order_by(PunchReview.created_at.desc(),PunchReview.id.desc()).all())
    return points,rows[0] if rows else None,events


@bp.get("/ocorrencias/<int:user_id>/<day_text>")
@permission_required(Permission.PUNCH_VIEW)
def occurrence_detail(user_id,day_text):
    subject,day=_scoped_subject(user_id,day_text)
    points,row,events=_day_context(subject,day)
    if not points:
        abort(404)
    marked=simulated_ids(points)
    rendered_events=[(entry,_open(entry.note)["text"]) for entry in events]
    return render_template("admin/ocorrencia_detalhe.html",subject=subject,day=day,
                           points=points,row=row,events=rendered_events,synthetic=marked,
                           nonce=str(uuid4()),local_time=_local_time,
                           can_review=g.admin_user.can(Permission.PUNCH_REVIEW))


@bp.post("/ocorrencias/<int:user_id>/<day_text>")
@permission_required(Permission.PUNCH_REVIEW)
def occurrence_record(user_id,day_text):
    subject,day=_scoped_subject(user_id,day_text)
    if not _day_context(subject,day)[0]:
        abort(404)
    action=request.form.get("action","")
    note=request.form.get("note","").strip()
    nonce=request.form.get("request_key","")
    try:
        if str(UUID(nonce)) != nonce:
            raise ValueError
    except ValueError:
        abort(400,"Solicitação inválida")
    if action not in {"justificativa","proposta_ajuste","revisado"} or not 3 <= len(note) <= 1000:
        abort(400,"Informe a ação e uma justificativa de 3 a 1000 caracteres")
    point_id=None
    proposed_type=None
    proposed_time=None
    if action=="proposta_ajuste":
        proposed_type=request.form.get("proposed_type","")
        proposed_time=request.form.get("proposed_time","")
        if proposed_type not in {"ENTRADA","SAIDA"}:
            abort(400,"Informe o tipo de marcação proposto")
        try:
            parsed=time.fromisoformat(proposed_time)
            if parsed.second or parsed.microsecond or parsed.tzinfo or len(proposed_time)!=5:
                raise ValueError
        except ValueError:
            abort(400,"Informe horário válido")
        raw=request.form.get("point_id","").strip()
        if raw:
            if not raw.isdigit():
                abort(400)
            point_id=int(raw)
            original=Ponto.query.filter(Ponto.id==point_id,Ponto.user_id==subject.id,
                                       Ponto.timestamp>=_utc_midnight(day),
                                       Ponto.timestamp<_utc_midnight(day+timedelta(days=1))).first()
            if original is None:
                abort(404)
    event=PunchReview(request_key=nonce,user_id=subject.id,company_id=subject.company_id,
                      worksite_id=subject.worksite_id,day=day,action=action,note=_seal({"text":note}),
                      point_id=point_id,proposed_type=proposed_type,proposed_time=proposed_time,
                      actor_user_id=g.admin_user.id)
    db.session.add(event)
    audit("punch_review.record","success",actor=g.admin_user,target_type="user_day",
          target_id=f"{subject.id}:{day.isoformat()}",metadata={"action":action})
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(409,"Solicitação já registrada")
    return redirect(url_for("admin.occurrence_detail",user_id=subject.id,day_text=day.isoformat()))
