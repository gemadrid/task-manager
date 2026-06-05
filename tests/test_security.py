

# @pytest.mark.parametrize("method,url", [
#     ("GET",    "/users/me"),
#     ("PATCH",  "/users/me"),
#     ("DELETE", "/users/me"),
#     ("GET",    "/tasks/"),
#     ("POST",   "/tasks/"),
#     ("GET",    "/tasks/1"),
#     ("PATCH",  "/tasks/1"),
#     ("DELETE", "/tasks/1"),
# ])

# def test_protected_endpoints_require_auth(client, method, url):
#     response = client.request(method, url)
#     assert response.status_code == 401