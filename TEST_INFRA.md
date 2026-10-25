# Infraestrutura de testes — DreeZy-HUB 2.1.0

Revisão de 25/10/2026. As metas anteriores de uma arquitetura modular futura foram substituídas pela descrição dos testes realmente existentes.

A suíte completa está publicada em [tests/](tests/). Evidências da revalidação: [reports/2026-10-25/](reports/2026-10-25/).

## Ambiente

- Python 3.12.
- Lupa 2.8 / Lua 5.5 somente nas suítes antigas.
- Luau 0.744 para compilação e integração do script real, sem converter continue.
- Ferramentas oficiais instaláveis por tests/setup_luau.py no Windows, com versão e SHA-256 fixados.

## Executar

~~~powershell
python -m pip install -r requirements-dev.txt
python tests/setup_luau.py
python tests/run_all.py
~~~

LUAU_BIN e LUAU_COMPILER permitem usar instalações existentes. Se o compilador não estiver disponível, a validação falha explicitamente; não aprova por substituição textual.

run_all.py grava logs e results.json em .test-results, ou na pasta passada por --output. Ele também verifica a sintaxe Python.

## Suítes presentes

| Suíte | Casos | Alcance |
|---|---:|---|
| run_tests.py | 18 | Tipos, instâncias, serviços e primitivas do mock |
| test_challenger_m1.py | 36 | Matemática, câmera, eventos e verificador |
| test_challenger_probe.py | 20 | JSON, arquivos virtuais e desenhos |
| test_challenger_v2_deep.py | 10 | Limites e estresse do mock |
| test_syntax_regressions.py | 7 | Continue fora de loop, strings, tipos Luau, erros e compilador ausente |
| test_hub.py + test_cases.lua | 52 | Programa completo, recursos, configurações, ciclos de vida e limites de trabalho |

Total validado: **143 casos**, com zero falhas. Além deles, os quatro arquivos Lua são compilados pelo verificador nativo.

## Integração

test_hub.py concatena o mock, a extensão de tempo virtual e o **fonte original integral** dentro de um programa temporário. Executa esse programa no interpretador Luau real. Não reescreve continue, strings ou fluxo de controle.

mock_scheduler.lua fornece agendamento determinístico, cancelamento, entrada sintética, consultas espaciais e contadores. Chamadas de rede são bloqueadas. O mock registra erros de callbacks e tarefas, para que um pcall interno não os esconda dos testes.

Cobertura funcional inclui:

- bootstrap, ausência de Drawing e falha de serviço;
- execução duplicada, remoção de interface e encerramento;
- cursor, escopo de alvos, FOV e cache de amizade;
- restauração de colisões, hitbox e Shift Lock;
- frequência de recursos em clientes simulados de 60 e 144 Hz;
- ESP sob demanda e limite de inventário;
- consultas de mapa vazio, orçamento de estruturas e cancelamento;
- cliques, teclado/mouse, foco e reativação rápida;
- roundtrip de opções, atalhos e listas;
- formato legado, backup, tipos inválidos e rollback;
- 50 alternâncias de recursos e reconstruções de favoritos;
- efeito decorativo prolongado sem acúmulo de conexões concluídas.

Não foi calculado percentual de cobertura por linha ou branch.

## Benchmark

~~~powershell
python tests/benchmark_hub.py --before CAMINHO_DO_ORIGINAL --after RespawnHUD.lua --luau CAMINHO_DO_LUAU --output benchmark.json
~~~

São cenários determinísticos de 10 s a 60 quadros/s, com semente fixa. Medem callbacks, desenhos, tarefas e consultas, não FPS nem tempo de execução do cliente Roblox.

O contador de chamadas de rede da versão antiga indica tentativa bloqueada pelo mock, sem acesso real ao GitHub durante a simulação. Tarefas pendentes incluem tweens simulados; não devem ser interpretadas como contagem de threads do cliente real.

## Limites

O simulador não reproduz toda a API Roblox, física, replicação, permissões de executores ou eventuais bloqueios de jogo. A compilação prova validade sintática para a versão usada, sem provar compatibilidade integral com todas as versões do cliente.

