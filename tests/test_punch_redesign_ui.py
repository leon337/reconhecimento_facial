"""Regressão da interface de ponto: sem alterar a captura facial ou as rotas."""
import unittest
from pathlib import Path
from main import create_app


class PunchRedesignUITests(unittest.TestCase):
    def test_punch_redesign_preserves_camera_and_routes(self):
        app = create_app({"TESTING": True})
        with app.test_client() as client:
            response = client.get("/punch")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        for required in (
            'lang="pt-BR"', 'id="punch-app"', 'id="start-camera"',
            'id="start-verification"', 'id="camera-shell"', 'id="video"',
            'id="tipo"', 'id="challenge-panel"', 'id="elapsed-time"',
            'id="status"', 'data-csrf-token="', 'punch-redesign.css',
            'Nenhuma foto da galeria é aceita.',
        ):
            self.assertIn(required, html)
        self.assertNotIn('type="file"', html)
        self.assertNotIn('type="submit"', html)

    def test_layout_keeps_secure_live_camera_contract(self):
        root = Path(__file__).resolve().parents[1]
        html = (root / "templates/punch.html").read_text()
        js = (root / "static/punch.js").read_text()
        css = (root / "static/punch-redesign.css").read_text()
        for value in (
            'data-camera-state="idle"', 'class="punch-camera-shell hidden"',
            'class="punch-video hidden"', 'name="tipo"',
            'value="ENTRADA"', 'value="SAIDA"',
        ):
            self.assertIn(value, html)
        for value in (
            "setCameraState(true)", "setCameraState(false)",
            "captureBurst", "challenge_id", "window.isSecureContext", "getUserMedia",
        ):
            self.assertIn(value, js)
        self.assertNotIn("FileReader", js)
        self.assertIn(".punch-camera-shell", css)
        self.assertIn(":focus-visible", css)
        self.assertIn("@media (max-width: 390px)", css)


if __name__ == "__main__":
    unittest.main()
