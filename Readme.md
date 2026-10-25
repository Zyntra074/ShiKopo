# ShiKopo 2.1.2

## Nova interface em estudo

O [protótipo visual interativo](prototypes/README.md) apresenta as variantes Workspace e Compacto, com módulos e uma cena demonstrativa. A proposta está em avaliação; o script de uso continua na versão 2.1.2.

Revisão de 25/10/2026, publicada em `Zyntra074/ShiKopo` com os testes e evidências, com correções funcionais, encerramento de recursos e otimizações de trabalho. O programa continua distribuído em **ShiKopo.lua**, um único arquivo, com blocos internos e um runtime compartilhado.

## Arquivo principal

O arquivo principal agora é **[ShiKopo.lua](ShiKopo.lua)**, anteriormente chamado RespawnHUD.lua. Atualize referências e links que ainda apontem para o nome anterior. Para reexecução após teleporte, use uma cópia atualizada em `ShiKopo/ShiKopo.lua`.

## Nome e arquivos anteriores

O hub agora se chama **ShiKopo**, incluindo menu, notificações e diagnóstico. As novas configurações e favoritos ficam em `ShiKopo/`. Quando há arquivos em `DreeZyHub/` e o destino ainda não existe, a inicialização copia `Config.json`, `Config.json.bak` e `Favorites.json` sem remover os originais. Os arquivos novos têm prioridade; o carregamento de configurações continua manual. Falhas na importação são registradas no diagnóstico.

A cópia de reexecução após teleporte deve ser atualizada pelo usuário em `ShiKopo/ShiKopo.lua`; código antigo não é importado automaticamente.

## Usar a versão corrigida

1. Use **ShiKopo.lua da branch main de [Zyntra074/ShiKopo](https://github.com/Zyntra074/ShiKopo/blob/main/ShiKopo.lua)**. Este é o repositório oficial deste trabalho; comandos antigos que apontam para outros repositórios podem carregar outra versão.
2. Se a versão antiga já está ativa, reconecte ao jogo antes do primeiro teste. Não é possível desfazer de fora as tarefas que a versão antiga não registrou.
3. Execute o conteúdo do arquivo local no ambiente de execução compatível que você já utiliza.
4. Em **Configs → Desempenho**, selecione **Econômico** se a prioridade for reduzir o custo dos recursos visuais.
5. Ao terminar, use **Descarregar HUB**. A versão corrigida também limpa seus recursos se sua interface principal for removida.

**Right Shift** abre/fecha o menu. **P**, por padrão, solta o cursor. Não há atalho Ctrl+R para respawn nesta versão.

Esta revisão não altera qualidade gráfica, resolução ou configurações do jogo. A otimização reduz o trabalho do próprio script.

## Perfis de desempenho

| Perfil | ESP | High Alert | Minimapa | Verificação da hitbox | Limite de estruturas do mapa |
|---|---:|---:|---:|---:|---:|
| Econômico | 20/s | 10/s | 10/s | aproximadamente 6,7/s | 150 |
| Equilibrado, padrão | 30/s | 20/s | 20/s | 10/s | 300 |
| Alta atualização | 60/s | 30/s | 30/s | 20/s | 600 |

São limites de atualização, não garantias de FPS. A câmera do Aimbot e o Shift Lock continuam acompanhando os quadros do cliente enquanto habilitados. Aquisição/validação de alvo usa intervalo próprio de aproximadamente 100 ms, e consultas de visibilidade repetidas têm cache curto.

- Recursos desligados não mantêm seus jobs de atualização por quadro.
- Neve decorativa começa desligada; pode ser ativada em Configs.
- Inventário do ESP só aloca desenhos quando solicitado e próximo da câmera.
- A lista de inventário é consultada a cada 0,5 s, enquanto sua posição visual acompanha a atualização do ESP.
- O minimapa usa consulta espacial limitada e cache. Cenários muito densos podem aparecer simplificados conforme o orçamento do perfil.
- Intervalos de clique pequenos estão sujeitos aos quadros do cliente e à duração do pulso. Não há promessa de 1.000 cliques/s.

O botão **Medir custo das funções** habilita a medição de custo dos jobs. **Mostrar diagnóstico** imprime contadores e erros no console do ambiente de execução. O campo ProfiledCalls separa as chamadas medidas das chamadas totais; a instrumentação começa desligada.

## Funcionalidades

- Respawn na posição de morte, com cancelamento por personagem e estado.
- Aimbot de câmera/cursor com FOV, suavização, partes aleatórias e filtros.
- Expansão de partes R6/R15 com restauração das propriedades.
- AutoShot e Auto Click com atalhos de teclado ou mouse e liberação de entrada ao desligar.
- ESP de caixas, nomes, vida, linhas e inventário.
- High Alert com bordas e setas.
- Minimapa de jogadores, elevação e estruturas.
- TP para jogador, TP por clique e destaque de jogadores para seleção.
- Anti-AFK, Shift Lock livre, favoritos e configurações.

“KillAuraCore” é o nome interno do recurso **Tp player**. Ele segue o alvo por teleporte e modifica colisões; não implementa ataque melee nesse bloco.

Sem a API Drawing, o restante da interface inicializa. Os controles de ESP/High Alert informam indisponibilidade e revertem o switch quando ativados.

## Configurações e favoritos

O salvamento é manual pelos botões de Configs:

- ShiKopo/Config.json: esquema 2, com valores e atalhos.
- ShiKopo/Config.json.bak: cópia anterior quando disponível e decodificável.
- ShiKopo/Config.json.tmp: etapa de escrita, removida após sucesso se o executor oferece exclusão.
- ShiKopo/Favorites.json: favoritos e sua ordem.

Esses caminhos são relativos ao espaço de arquivos do executor, não necessariamente à pasta Downloads.

São persistidos 53 controles, incluindo listas de exceção, partes de hitbox, alvo do Auto Click, alvo/time do TP, tamanho de nomes e perfil de desempenho. Atalhos são armazenados separadamente no mesmo esquema.

O carregamento aceita JSON legado e Base64 legado. Valores são validados antes da aplicação; recursos são desativados durante a mudança e reativados depois. Em falha de aplicação, o gerenciador tenta restaurar o estado anterior e informa erro. Em JSON principal ilegível, tenta o backup. Não há garantia de escrita atômica em APIs de executor.

## Reconectar e reexecutar

Reconectar continua disponível. A reexecução automática está desligada por padrão e **não baixa mais código de um branch remoto mutável**.

Para utilizá-la, o executor precisa oferecer fila após teleporte e leitura de arquivos. Salve uma cópia atualizada de ShiKopo.lua no caminho **ShiKopo/ShiKopo.lua dentro do espaço de arquivos do executor**. A opção agenda o conteúdo dessa cópia local. Se ela ou as APIs não estiverem disponíveis, a interface informa o motivo.

Alterar o arquivo em Downloads não atualiza automaticamente a cópia do espaço do executor.

## Fluxo de manutenção

Por solicitação do proprietário em 25/10/2026, o GitHub é a fonte oficial do script. Cada alteração concluída deve ser validada e publicada neste repositório junto com testes e documentação pertinentes. As cópias locais são temporárias para preparação e testes. Consulte [AGENTS.md](AGENTS.md).

A suíte está em [tests/](tests/). A validação atual está em [reports/2026-10-25-shikopo-lua/](reports/2026-10-25-shikopo-lua/); a troca da marca foi validada em [reports/2026-10-25-shikopo/](reports/2026-10-25-shikopo/); a entrega anterior permanece como evidência histórica em [reports/2026-10-25/](reports/2026-10-25/).

## Estrutura real

- ShiKopo.lua: runtime, 12 blocos funcionais, persistência e interface.
- tests/mock_roblox.lua: tipos e serviços básicos simulados.
- tests/mock_scheduler.lua: tempo virtual, entrada e consultas espaciais para integração.
- tests/test_cases.lua: 59 cenários de integração.
- tests/test_hub.py: executa o programa completo em Luau nativo.
- tests/run_all.py: executa todas as suítes.
- tests/verify_syntax.py: usa luau-compile sem modificar o fonte.
- tests/test_syntax_regressions.py: regressões do verificador.
- tests/benchmark_hub.py: comparação de contadores entre duas versões.
- tests/setup_luau.py: instalação opcional do compilador oficial fixado para testes Windows.
- requirements-dev.txt: dependências dos testes antigos.
- PROJECT.md, TEST_INFRA.md e CHANGELOG.md: estado do projeto e validação.

Não existem diretórios modules/ ou ui/ nesta distribuição.

## Executar testes de desenvolvimento

Ambiente validado: Python 3.12, Lupa 2.8 e Luau 0.744. O script Roblox não precisa de Python; estas ferramentas servem apenas aos testes.

No Windows, com Python disponível:

~~~powershell
python -m pip install -r requirements-dev.txt
python tests/setup_luau.py
python tests/run_all.py
~~~

O instalador baixa o pacote oficial do Luau, confere o SHA-256 fixado e o coloca em .tools/luau. Não instala executores Roblox. Também é possível definir LUAU_BIN e LUAU_COMPILER para ferramentas já disponíveis.

Resultado validado nesta revisão: **150 casos aprovados** — 84 existentes, 59 de integração e 7 regressões sintáticas — além da compilação dos quatro arquivos Lua.

O simulador permite testar inicialização, cancelamentos, alternâncias, configurações e contadores. Não reproduz física, permissões, rede ou FPS de um cliente real.

## Comparação de trabalho

Em simulação determinística de 10 s a 60 quadros/s:

| Cenário | Antes | Depois |
|---|---:|---:|
| Ocioso: callbacks dos serviços de quadro | 5.400 | 0 |
| Ocioso: desenhos ativos | 25 | 0 |
| ESP de 20 jogadores, sem inventário: desenhos totais | 485 | 100 |
| Mapa vazio com terreno ligado: enumerações completas | 601 | 0 |
| Mapa vazio: consultas espaciais limitadas | 0 | 10 |

A queda de trabalho está demonstrada nesses cenários. **O ganho de FPS no Roblox não foi medido** e varia conforme jogo, executor, dispositivo e recursos ativos.

As escolhas seguem a orientação de reservar o render step para trabalho necessário a cada quadro: [Roblox Task Scheduler](https://create.roblox.com/docs/performance-optimization/microprofiler/task-scheduler). O mapa usa a consulta documentada em [WorldRoot:GetPartBoundsInRadius](https://create.roblox.com/docs/reference/engine/classes/WorldRoot#GetPartBoundsInRadius).

## Origem e licença

A cópia recebida menciona DreeZy como autor e dois repositórios diferentes. A relação entre eles não foi confirmada. O proprietário autorizou a publicação desta revisão em `Zyntra074/ShiKopo`; isso não confirma a autoria ou licença do código original.

A distribuição recebida não possui texto completo de licença. Não foi criada uma licença em nome do autor. Os avisos originais sobre detecção e consequências do uso de scripts continuam relevantes; não há garantia de indetectabilidade ou compatibilidade com todos os executores.

