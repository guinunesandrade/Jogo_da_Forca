from Funções import *

try:
    tabela_usuarios('Jogadores.sqlite')
    préjogo()
except (KeyboardInterrupt, RuntimeError):
    print(f'\n{red_text("Conexão interrompida pelo próprio usuário! Encerrando jogo...")}')
