import json
import random
import sqlite3


def import_word():
    # Abrindo o arquivo contendo as palavras e garantindo que já seja fechado com o "with"
    with open('Words.json', 'r') as words:
        fwords = json.load(words)
        # print(fwords)

    palavras = fwords['Palavras']

    # A variável word representa a palavra aleatória do jogo e deve ser tratada como global
    # para poder ser usada nas outras funções
    global word
    global tema_aleatório
    global subtema_aleatório

    # Salvar cada tema como um item de uma lista
    temas = list(palavras.keys())
    # print(temas)

    # Selecionar um tema aleatório da lista temas
    tema_aleatório = random.choice(temas)
    # print(tema_aleatório)

    # Salvar cada subtema como um item de uma lista
    subtemas = list(palavras[tema_aleatório].keys())

    # Selecionar um subtema aleatório da lista subtemas
    subtema_aleatório = random.choice(subtemas)
    # print(subtema_aleatório)

    # Salvar as palavras de um determinado subtema dentro de um tema em forma de lista
    palavras_tema_subtema = palavras[tema_aleatório][subtema_aleatório]

    # Selecionar uma palavra aleatória para ser a palavra do jogo
    word = random.choice(palavras_tema_subtema).upper()
    return word, tema_aleatório, subtema_aleatório


def tabela_usuarios(banco_de_dados):
    conn = sqlite3.connect(banco_de_dados)
    cur = conn.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS User 
            (
            id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name        TEXT UNIQUE,
            victories   INTEGER,
            defeats     INTEGER
            )
        '''
    )
    cur.close()


def registro_usuario(banco_de_dados):
    global nick
    while True:
        nick = input('Digite um nome de usuário: ').upper().strip()
        if nick.strip() != "":
            break
        else:
            print(red_text('ERRO! Você não pode deixar em branco o nome de usuário.'))
    conn = sqlite3.connect(banco_de_dados)
    cur = conn.cursor()
    cur.execute('INSERT OR IGNORE INTO User (name, victories, defeats) VALUES ( ?, ?, ? )', (nick, 0, 0))
    conn.commit()
    cur.close()


def préjogo():
    while True:
        layout_inicial()
        try:
            option = int(input(f'Digite uma opção acima ({green_text("1")}, '
                               f'{yellow_text("2")} ou {red_text("3")}): '))
            print()
        except (KeyboardInterrupt, RuntimeError):
            print(red_text('\nConexão interrompida pelo próprio usuário! Programa encerrando...'))
            exit()
        except (TypeError, ValueError):
            print(red_text('ERRO! Digite um número disponível nas opções!'))
            continue
        else:
            if option == 1:
                registro_usuario('Jogadores.sqlite')
                while True:
                    try:
                        layout_game_level()
                        dificuldade = int(input(f'Em qual dificuldade você deseja jogar, {green_text(nick)}? '
                                                f'({green_text("1")}, {yellow_text("2")}, {red_text("3")} ou '
                                                f'{blue_text("4")}): '))
                        print()
                    except (KeyboardInterrupt, RuntimeError):
                        print(red_text('\nConexão interrompida pelo próprio usuário! Programa encerrando...'))
                        exit()
                    except (TypeError, ValueError):
                        print(red_text('ERRO! Digite um número disponível nas opções!'))
                        continue
                    else:
                        if 1 <= dificuldade <= 3:
                            personalization('Bacana! Vamos jogar!'.upper())
                        if dificuldade == 1:
                            jogo(tema=True, subtema=True)
                            break
                        elif dificuldade == 2:
                            jogo(tema=True)
                            break
                        elif dificuldade == 3:
                            jogo()
                            break
                        elif dificuldade == 4:
                            print(f'{green_text("Fácil:")} No nível fácil, você terá duas dicas: '
                                  f'uma sobre o tema e outra sobre o "subtema".\n'
                                  f'Por exemplo, tema carro e subtema modelo.\n'
                                  f'{yellow_text("Médio:")} No modo médio, você terá apenas uma dica'
                                  f', referente ao tema, deixando oculto qual será o subtema.\n'
                                  f'Por exemplo, tema carro, podendo o subtema ser modelo, marca, etc.\n'
                                  f'{red_text("Difícil:")} No difícil, você não receberá nenhuma dica e terá que '
                                  f'advinhar a palavra sem saber o tema e o subtema nos quais ela se encaixa.')
                        else:
                            print(red_text('ERRO! Digite um número entre 1 e 4!'))

            elif option == 2:
                # Criando e formatando a tabela aqui na IDE
                personalization('TABELA DE JOGADORES')
                print(f'{"Jogador":<15}{"Vitórias":<10}{"Derrotas":>15}{"Taxa de Vitórias":>20}\n')

                # Acessar database e printar cada célula na tabela acima
                conn = sqlite3.connect('Jogadores.sqlite')
                cur = conn.cursor()
                cur.execute('SELECT *, ROUND((CAST(victories as REAL) / (victories + defeats)) * 100, '
                            '2) As victories_rate '
                            ' FROM User'
                            '   ORDER BY 5 DESC')
                result = cur.fetchall()
                for row in result:
                    if not str(row[4]) == 'None':
                        print(f'{row[1]:<15} {row[2]:<10} {row[3]:>8} {str(row[4]):>15} %')
                    else:
                        print(f'{row[1]:<15} {row[2]:<10} {row[3]:>8} {0.0:>15} %')
                cur.close()

            # Encerrando o programa
            elif option == 3:
                break
            else:
                print(red_text('ERRO! Digite um número entre 1 e 3!'))
    print(green_text('Obrigado por jogar! Volte sempre!'.upper()))


def layout_inicial():
    print()
    personalization('BEM VINDO AO JOGO DA FORCA')
    print(f'{green_text("1 - JOGAR")}\n'
          f'{yellow_text("2 - CONSULTAR RANKING")}\n'
          f'{red_text("3 - SAIR")}\n')


def jogo(tema=False, subtema=False):
    # Criando posições da forca como itens de uma lista
    forca = ['''
----- 
  |
  O    ''',
             '''
-----
  |
  O
  |    ''',
             '''
-----
  |
  O
  |
 / \   ''',
             '''   
-----
  |
  O
 /|\
\ 
 /\
 \ '''
             ]

    letras_certas = []
    letras_erradas = []
    c_derrota = -1

    # Importando palavra aleatória com o seu tema e subtema.
    import_word()

    # Criando a palavra oculta com base na quantidade de letras que há na palavra importada
    palavra_oculta = list('_' * len(word))

    while True:
        # Jogo no modo Fácil
        if tema and subtema:
            print(f'\n{green_text("DICA:")} A palavra é um(a) {blue_text(subtema_aleatório)} '
                  f'de um(a) {blue_text(tema_aleatório)}.')

        # Jogo no modo Médio
        elif tema:
            print(f'\n{green_text("DICA:")} {blue_text(tema_aleatório)}.')

        # Jogo no modo difícil
        else:
            pass

        # Pula uma linha
        print()

        # printando a palavra oculta em formato de string já editada
        print(f'{blue_text("Palavra:")} {",".join(palavra_oculta).replace(",", "")}')

        # Printando a quantidade de vezes que o usuário ainda pode errar
        chances = (len(forca) - 1) - c_derrota
        if chances == 1:
            print(yellow_text(f'Você ainda pode errar {chances} vez!'))
        elif chances == 0:
            print(yellow_text(f'Você não pode mais errar, senão você perde!'))
        else:
            print(yellow_text(f'Você ainda pode errar {chances} vezes!'))

        # A cada rodada printa a posição em que se encontra a forca
        # desde o momento em que o usuário erra a primeira letra
        if c_derrota >= 0:
            print(f'\n{yellow_text(forca[c_derrota].strip())}\n')

        # Printa as letras que o usuário acertou até o momento
        if len(letras_certas) > 0:
            print(green_text('Letras certas: '), end='')
            for c, letra in enumerate(letras_certas):
                if letra not in letras_certas[:c]:
                    if c == 0:
                        print(letra, end=' ')
                    else:
                        print(f'- {letra}', end=' ')
            print()

        # Printa as letras que o usuário errou até o momento
        if len(letras_erradas) > 0:
            print(f'{red_text("Letras erradas: ")}{",".join(letras_erradas).replace(",", " - ")}')

        # Usuário escolhe uma letra a cada rodada
        while True:
            while True:
                while True:
                    letra = input('\nEscolha uma letra: ').upper().strip()
                    if len(letra) > 1:
                        print(red_text('Erro! Você só pode digitar uma letra por vez.'))
                    else:
                        break
                if letra.isalpha():
                    break
                else:
                    print(red_text('Erro! Você não pode digitar um caractere '
                                   'que não seja uma letra, nem deixar em branco.'))
            if letra not in letras_certas and letra not in letras_erradas:
                if letra in word:
                    print(f'A letra {green_text(letra)} pertence à palavra')
                else:
                    print(f'A letra {red_text(letra)} não pertence à palavra')
                break
            else:
                print(red_text(f'Erro! A letra {letra} já foi escolhida anteriormente.'))

        # Adiciona algum membro do corpo à medida que uma letra errada é escolhida
        if letra not in word:
            letras_erradas.append(letra)
            c_derrota += 1

        # Se a letra escolhida estiver certa, adiciona ela à lista de letras certas e substitui
        # o(s) espaço(s) ocultos da palavra oculta pela letra em sua(s) respectiva(s) posição(ões)
        else:
            for p, l in enumerate(word):
                if l == letra:
                    letras_certas.append(letra)
                    palavra_oculta[p] = letra

        # Encerramento do jogo e atualização na database do n.º derrotas do jogador caso ele tenha perdidp
        if c_derrota == len(forca):
            print()
            derrota()
            print(f'A palavra era {blue_text(word)}')
            conn = sqlite3.connect('Jogadores.sqlite')
            cur = conn.cursor()
            cur.execute('SELECT defeats FROM User WHERE name = ? ', (nick,))
            n_derrotas = cur.fetchone()[0]
            cur.execute('UPDATE User SET defeats = ? WHERE name = ? ', (n_derrotas + 1, nick))
            conn.commit()
            cur.close()
            break

        # Encerramento do jogo e atualização na database do nº de vitórias do jogador caso ele tenha vencido.
        elif len(letras_certas) == len(word):
            print()
            vitória()
            print(f'\nA palavra era {blue_text(word)}.')
            conn = sqlite3.connect('Jogadores.sqlite')
            cur = conn.cursor()
            cur.execute('SELECT victories FROM User WHERE name = ? ', (nick,))
            n_vitorias = cur.fetchone()[0]
            cur.execute('UPDATE User SET victories = ? WHERE name = ? ', (n_vitorias + 1, nick))
            conn.commit()
            cur.close()
            break
    pass


def vitória():
    print(green_text('Você acertou!'))


def derrota():
    print(red_text('Você perdeu!'))


def personalization(text):
    print(blue_text('-' * 60))
    print(blue_text(text.center(60)))
    print(blue_text('-' * 60))


def red_text(text):
    x = f'\033[1;31m{text}\033[m'
    return x


def green_text(text):
    x = f'\033[1;32m{text}\033[m'
    return x


def yellow_text(text):
    x = f'\033[1;33m{text}\033[m'
    return x


def blue_text(text):
    x = f'\033[1;34m{text}\033[m'
    return x


def layout_game_level():
    print()
    personalization('DIFICULDADE DO JOGO')
    print(f'{green_text("1 - FÁCIL")}\n'
          f'{yellow_text("2 - MÉDIO")}\n'
          f'{red_text("3 - DIFÍCIL")}\n'
          f'{blue_text("4 - EXPLICAÇÃO DE CADA DIFICULDADE")}\n')
