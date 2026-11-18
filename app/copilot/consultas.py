"""Consultas conversacionais determinísticas, somente leitura e restritas ao escopo administrativo.

Não envia dados pessoais para modelos externos. Não executa SQL gerado pelo usuário.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from flask import abort, g, jsonify, make_response, render_template, request, session, url_for
from flask_wtf.csrf import generate_csrf
from sqlalchemy import func

from app.admin.auth import permission_required
from app.admin.simulation import simulated_ids
from app.attendance_reporting import summarize_punches
from app.copilot import bp
from app.models import Employee, Ponto, User
from app.rbac import Permission

RECIFE = ZoneInfo("America/Recife")
MAX_RESULT = 20
MAX_PUNCHES = 3000


def _normalize(text):
    text = unicodedata.normalize("NFKD", text.casefold())
    return "".join(c for c in text if not unicodedata.combining(c))


def _scope(query, model):
    company_id = session.get("admin_company_id")
    worksite_id = session.get("admin_worksite_id")
    query = query.filter(model.company_id.is_(None) if company_id is None else model.company_id == company_id)
    if company_id is not None and worksite_id is not None:
        query = query.filter(model.worksite_id == worksite_id)
    return query


def _employee_query():
    return _scope(Employee.query, Employee)


def _user_query():
    return _scope(User.query.filter(User.employee_id.isnot(None)), User)


def _day_range(text):
    today = datetime.now(RECIFE).date()
    if "ontem" in text:
        return today - timedelta(days=1), today - timedelta(days=1)
    if "semana" in text or "ultimos 7" in text:
        return today - timedelta(days=6), today
    if "mes" in text:
        return today.replace(day=1), today
    match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
    if match:
        from datetime import date
        try:
            day = date.fromisoformat(match.group(1))
        except ValueError:
            raise ValueError("Data inválida. Use AAAA-MM-DD.")
        if day > today:
            raise ValueError("Consulte datas até hoje.")
        return day, day
    return today, today


def _utc_bounds(start, end):
    lower = datetime.combine(start, time.min, tzinfo=RECIFE).astimezone(timezone.utc).replace(tzinfo=None)
    upper = datetime.combine(end + timedelta(days=1), time.min, tzinfo=RECIFE).astimezone(timezone.utc).replace(tzinfo=None)
    return lower, upper


def _records(start, end):
    allowed = _user_query().with_entities(User.id)
    low, high = _utc_bounds(start, end)
    return Ponto.query.filter(
        Ponto.user_id.in_(allowed),
        Ponto.timestamp >= low,
        Ponto.timestamp < high,
    ).order_by(Ponto.timestamp.desc(), Ponto.id.desc()).limit(MAX_PUNCHES + 1).all()


def answer(question, actor):
    q = _normalize(question.strip())
    if not q or len(question) > 240:
        raise ValueError("Escreva uma pergunta com até 240 caracteres.")
    if re.search(r"\b(apague|delete|exclua|altere|edite|cadastre|registre|corrija|justifique|aprovar|aprova)\b", q):
        return {"answer": "Este assistente é somente leitura. Nenhum cadastro ou ponto foi alterado.", "rows": [], "source": "Política de acesso"}
    if any(word in q for word in ("senha", "biometria", "foto facial", "rosto", "cpf", "endereco")):
        return {"answer": "Informações sensíveis e biométricas não são disponibilizadas por este assistente.", "rows": [], "source": "Política de privacidade"}

    is_punch = any(word in q for word in ("ponto", "pontos", "marcacao", "marcacoes", "entrada", "saida", "atraso", "jornada", "ocorrencia"))
    if is_punch and not actor.can(Permission.PUNCH_VIEW):
        abort(403)
    if not is_punch and not actor.can(Permission.USERS_VIEW):
        abort(403)

    if not is_punch:
        if not any(word in q for word in ("funcionario", "funcionaria", "colaborador", "equipe", "cadastro", "ativos")):
            return {"answer": "Posso consultar funcionários, marcações de ponto e indicadores de jornada. Experimente um dos exemplos.", "rows": [], "source": "Catálogo de consultas"}
        if "quantos" in q or "total" in q:
            active = _employee_query().filter(Employee.active.is_(True)).count()
            total = _employee_query().count()
            return {"answer": f"Há {total} funcionário(s) cadastrado(s) no seu escopo, dos quais {active} ativo(s).", "rows": [], "source": "Cadastro de funcionários"}
        users = _employee_query().order_by(Employee.name, Employee.id).limit(MAX_RESULT + 1).all()
        if len(users) > MAX_RESULT:
            return {"answer": f"Há mais de {MAX_RESULT} funcionários. Refine sua consulta; a lista foi limitada.", "rows": [], "source": "Cadastro de funcionários"}
        return {"answer": f"Encontrei {len(users)} funcionário(s) no seu escopo.", "rows": [{"nome": u.name, "matricula": u.registration or "Não informada", "cargo": u.job_title or "Não informado", "situacao": "Ativo" if u.active else "Inativo"} for u in users], "source": "Cadastro de funcionários"}

    start, end = _day_range(q)
    if (end - start).days > 30:
        raise ValueError("Período máximo de 31 dias.")
    points = _records(start, end)
    if len(points) > MAX_PUNCHES:
        return {"answer": "O período ultrapassa o limite de 3.000 marcações. Refine a consulta.", "rows": [], "source": "Registros de ponto"}
    if any(word in q for word in ("atraso", "jornada", "ocorrencia", "incomplet")):
        daily = summarize_punches(points, start, end)
        if "atraso" in q:
            rows = [r for r in daily if any("Entrada após" in occurrence for occurrence in r["occurrences"])]
        else:
            rows = [r for r in daily if r["issues"] or r["occurrences"]]
        if len(rows) > MAX_RESULT:
            return {"answer": f"Encontrei {len(rows)} jornada(s) para conferência. Refine o período.", "rows": [], "source": "Apuração indicativa de jornada"}
        return {"answer": f"Encontrei {len(rows)} jornada(s) com indicadores para conferência. Não constitui apuração trabalhista definitiva.", "rows": [{"funcionario": r["user"].name or r["user"].username, "dia": r["day"].isoformat(), "indicadores": ", ".join(r["issues"] + r["occurrences"])} for r in rows], "source": "Apuração indicativa de jornada"}
    if "quantos" in q or "total" in q:
        return {"answer": f"Há {len(points)} marcação(ões) de {start:%d/%m/%Y} a {end:%d/%m/%Y} no seu escopo.", "rows": [], "source": "Registros de ponto"}
    if len(points) > MAX_RESULT:
        return {"answer": f"Há {len(points)} marcações. Exibindo somente as {MAX_RESULT} mais recentes.", "rows": _point_rows(points[:MAX_RESULT]), "source": "Registros de ponto"}
    return {"answer": f"Encontrei {len(points)} marcação(ões) entre {start:%d/%m/%Y} e {end:%d/%m/%Y}.", "rows": _point_rows(points), "source": "Registros de ponto"}


def _point_rows(points):
    synthetic = simulated_ids(points)
    return [{
        "funcionario": p.user.name or p.user.username,
        "tipo": p.tipo,
        "horario": p.timestamp.replace(tzinfo=timezone.utc).astimezone(RECIFE).strftime("%d/%m/%Y %H:%M:%S"),
        "origem": "Simulado" if p.id in synthetic else "Não identificada",
    } for p in points]


@bp.get("/consultas")
@permission_required(Permission.USERS_VIEW)
def assistant_consultas():
    response = make_response(render_template("admin/assistente_consultas.html", csrf_value=generate_csrf()))
    response.headers["Cache-Control"] = "no-store, private"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    return response


@bp.post("/consultas/perguntar")
@permission_required(Permission.USERS_VIEW)
def assistant_ask():
    if not request.is_json:
        return jsonify(error="Envie JSON."), 415
    if request.content_length is not None and request.content_length > 2048:
        return jsonify(error="Pergunta excede o limite permitido."), 413
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or set(body) != {"question"} or not isinstance(body["question"], str):
        return jsonify(error="Informe uma pergunta em texto."), 400
    try:
        result = answer(body["question"], g.admin_user)
    except ValueError as exc:
        return jsonify(error=str(exc)), 422
    response = jsonify(result)
    response.headers["Cache-Control"] = "no-store, private"
    return response
