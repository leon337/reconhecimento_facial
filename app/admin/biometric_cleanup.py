from flask import flash, redirect, session, url_for

from app.admin import bp
from app.admin.auth import permission_required
from app.admin.routes import _scoped_user_or_404
from app.biometrics import delete_private_image
from app.models import User, db
from app.observability import audit
from app.rbac import Permission


@bp.route("/users/<int:user_id>/biometric", methods=["DELETE", "POST"])
@permission_required(Permission.BIOMETRICS_MANAGE)
def remove_biometric(user_id):
    """Remove a biometria escolhida pelo administrador para resolver duplicidades."""
    user = _scoped_user_or_404(user_id)
    profile = user.biometric_profile
    object_key = profile.image_object_key if profile is not None else None
    had_biometric = profile is not None or bool(user.face_encoding)

    if profile is not None:
        db.session.delete(profile)
    user.face_encoding = None
    user.photo_url = None

    actor = db.session.get(User, session.get("admin_user_id"))
    audit(
        "admin.biometric.remove",
        "success" if had_biometric else "noop",
        actor=actor,
        target_type="user",
        target_id=user.id,
    )
    db.session.commit()
    delete_private_image(object_key)

    if had_biometric:
        flash("Biometria removida. Cadastre novamente usando a câmera ao vivo.", "success")
    else:
        flash("Este funcionário não possuía biometria cadastrada.", "error")
    return redirect(url_for("admin.list_users"))
