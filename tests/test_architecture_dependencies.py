import ast
from pathlib import Path


FORBIDDEN_DOMAIN_ROOTS = {
    "flask",
    "flask_sqlalchemy",
    "sqlalchemy",
    "app.application",
    "app.infrastructure",
    "app.web",
}

FORBIDDEN_APPLICATION_ROOTS = {
    "flask",
    "flask_sqlalchemy",
    "sqlalchemy",
    "app.infrastructure",
    "app.models",
}


def imported_modules(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def assert_no_forbidden_imports(directory: Path, forbidden: set[str]):
    violations = []
    for path in sorted(directory.rglob("*.py")):
        for module in imported_modules(path):
            if any(module == root or module.startswith(root + ".") for root in forbidden):
                violations.append(f"{path}: {module}")
    assert violations == []


def test_domain_does_not_depend_on_framework_or_outer_layers():
    assert_no_forbidden_imports(Path("app/domain"), FORBIDDEN_DOMAIN_ROOTS)


def test_application_does_not_depend_on_framework_or_infrastructure():
    assert_no_forbidden_imports(Path("app/application"), FORBIDDEN_APPLICATION_ROOTS)


def test_infrastructure_is_the_only_new_layer_allowed_to_import_legacy_models():
    offenders = []
    for root in (Path("app/domain"), Path("app/application")):
        for path in sorted(root.rglob("*.py")):
            if "app.models" in imported_modules(path):
                offenders.append(str(path))
    assert offenders == []
