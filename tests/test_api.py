import requests

# Definir a URL base da API rodando no Docker
BASE_URL = "http://localhost:8000"

def run_test(test_name, test_function):
    """Executa um teste e imprime o resultado no terminal."""
    print(f"Executando: {test_name}...")
    try:
        test_function()
        print(f"{test_name} passou!\n")
    except AssertionError:
        print(f"{test_name} falhou!\n")

def test_home():
    """Testa se a API está ativa."""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "mensagem" in response.json()

def test_recomendacao_similar():
    """Testa a recomendação de notícias similares."""
    noticia_id = "7ae3dfbe-d48f-4cca-99ea-dbf80282fab2"
    response = requests.get(f"{BASE_URL}/recomendacao/similar/{noticia_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "noticia_id" in data
    assert "recomendacoes" in data
    assert isinstance(data["recomendacoes"], list)

def test_recomendacao_coldstart():
    """Testa a recomendação para novos usuários."""
    response = requests.get(f"{BASE_URL}/recomendacao/coldstart")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "recomendacoes" in data
    assert isinstance(data["recomendacoes"], list)

def test_recomendacao_novidades():
    """Testa a recomendação de notícias novas."""
    response = requests.get(f"{BASE_URL}/recomendacao/novidades")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "recomendacoes" in data
    assert isinstance(data["recomendacoes"], list)

if __name__ == "__main__":
    print("\nIniciando os testes da API...\n")
    
    run_test("Teste de disponibilidade da API", test_home)
    run_test("Teste de recomendação similar", test_recomendacao_similar)
    run_test("Teste de recomendação para novos usuários", test_recomendacao_coldstart)
    run_test("Teste de recomendação de novidades", test_recomendacao_novidades)

    print("Todos os testes finalizados!\n")
