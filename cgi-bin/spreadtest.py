import requests

response = requests.get(
    "https://docs.google.com/spreadsheets/d/1hht0h0BP-TeO_RHx07RF0UjK2VX-tcRU47bQ9FKS8Cw/export?gid=260382663&format=csv"
)
assert response.status_code == 200, "Wrong status code"
