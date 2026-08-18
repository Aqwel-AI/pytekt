from pytekt.physics import web_api


def test_library_info():
    info = web_api.library_info()
    assert info["app"] == "physics"
    assert "version" in info


def test_query_payload():
    payload = web_api.query_payload("kinetic energy mass=2 velocity=3")
    assert payload["output_value"] == 9.0


def test_pendulum_payload():
    payload = web_api.pendulum_payload(length=1.0, angle_deg=10.0, steps=50)
    assert len(payload["theta"]) == 51
