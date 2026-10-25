# Correções e desempenho — ShiKopo 2.1.0

Entrega original local de **25/10/2026**, agora publicada com os testes em `Zyntra074/ShiKopo`. Evidências: [reports/2026-10-25/](reports/2026-10-25/).

> Registro da revisão 2.1.0. A renomeação para ShiKopo 2.1.1 e seus 150 testes estão documentados no CHANGELOG.md e em reports/2026-10-25-shikopo/. Os hashes e contadores abaixo descrevem a revisão original.

## Resultado

O arquivo principal (atualmente ShiKopo.lua, antes RespawnHUD.lua) foi corrigido na própria pasta ShiKopo. Foram mantidas as cinco abas e os blocos de funcionalidades, com um runtime compartilhado para trabalho sob demanda, cancelamento e limpeza.

A suíte final aprovou **143 casos**, sem falhas: 84 existentes, 52 novos cenários de integração e sete regressões do verificador. Os quatro arquivos Lua também passaram pela compilação Luau nativa.

A versão original foi guardada em:

**C:\Users\Ekon\Downloads\ShiKopo_Correcoes_2026-10-25\original**

O principal dessa cópia tem o SHA-256:

49e72e0146692b36bc06d15fab97425331087e19e1cc3bc1b551b53c17d6dbca

## Redução de trabalho demonstrada

Comparação das duas versões no mesmo simulador, em Luau 0.744, com 10 segundos a 60 quadros/s e semente aleatória fixa:

| Cenário e medida | Original | Corrigido |
|---|---:|---:|
| Ocioso: conexões em eventos de quadro | 9 | 0 |
| Ocioso: callbacks desses eventos | 5.400 | 0 |
| Ocioso: desenhos ativos | 25 | 0 |
| Ocioso: neve ativa | 77 | 0 |
| ESP de 20 jogadores, sem inventário: desenhos totais | 485 | 100 |
| ESP de 20 jogadores: callbacks dos serviços de quadro | 5.400 | 600 |
| ESP de 20 jogadores: atualizações efetivas do novo ESP | — | 300 |
| Mapa vazio: enumerações completas do cenário | 601 | 0 |
| Mapa vazio: consultas espaciais limitadas | 0 | 10 |

Com inventário desligado, o conjunto por jogador passou de 23 para cinco desenhos, redução de aproximadamente **78% por jogador**. O total do cenário inclui os desenhos gerais da versão antiga.

Os callbacks nativos do job ESP ainda são recebidos a cada Heartbeat enquanto ativo; o runtime aplica o orçamento e executa o processamento de ESP a 30 Hz no perfil padrão. Ocioso não mantém esses jobs.

**Esses números medem trabalho e alocação no simulador. Não são porcentagens de ganho de FPS no Roblox.** Não houve execução em cliente real, jogo ou executor externo. A medição de FPS continua dependendo do ambiente em que você utiliza o script.

O contador NetworkCalls do benchmark registra uma tentativa remota da versão antiga bloqueada pelo mock e nenhuma da versão nova; não foi feita requisição real ao GitHub pelo código do hub durante os testes.

## O que mudou

### Encerramento e inicialização

- Flag de carregamento só é marcada após bootstrap bem-sucedido.
- Falhas de inicialização desfazem recursos e permitem nova tentativa.
- Reexecutar esta versão encerra sua instância anterior.
- “Descarregar HUB” e remoção da GUI encerram conexões, tarefas, desenhos e interfaces.
- Colisões, propriedades da hitbox, câmera do Shift Lock e entradas mantidas são restauradas.
- Conexões de conclusão de animações são desconectadas após uso.
- Reconstrução de favoritos não mantém listeners de entrada de linhas antigas.
- Tarefas de respawn, mapa e cliques possuem cancelamento para impedir trabalho antigo de interferir numa nova ativação.

Se a versão anterior à 2.1.0 já está rodando, ela não possui o registro de recursos necessário para uma limpeza completa de fora. Reconecte uma vez antes do primeiro teste.

### Desempenho das funções

- Recursos desligados não continuam recebendo suas rotinas de quadro.
- Câmera permanece em atualização por quadro quando habilitada; busca/validação de alvos tem frequência própria.
- FOV barato é verificado antes de raycasts na aquisição.
- Visibilidade, amizade e lista de jogadores têm caches adequados ao uso.
- Hitbox atualiza em frequência limitada e evita atribuições de propriedades já iguais.
- ESP aloca inventário apenas sob demanda, limita sua distância e consulta itens a cada 0,5 s.
- High Alert, ESP e minimapa possuem orçamento de frequência por perfil.
- Minimapa usa GetPartBoundsInRadius com limite de resultados e cache, sem GetDescendants por quadro.
- Mapa vazio respeita o intervalo mínimo entre consultas.
- Quantidade de estruturas e frames do minimapa é limitada; perfil menor simplifica cenários densos.
- Neve começa desligada; quando habilitada é limitada e não processa novas partículas com o menu oculto.
- Cronômetro de Anti-AFK só atualiza enquanto o recurso está ligado.
- Foi eliminada a consulta de jogadores que reconstruía dropdown a cada cinco segundos.
- Não foram alterados gráficos, resolução ou conteúdo do jogo.

### Correções funcionais

- Eliminada a chamada inexistente a UnfreezeCamera.
- Corrigido o escopo das variáveis de alvo do Aimbot.
- Sem Drawing, a inicialização termina; recursos dependentes informam indisponibilidade.
- Switches principais revertem seu estado em erro de callback.
- Binds funcionam com teclado/mouse e respeitam foco e captura de atalhos.
- Dígitos do teclado virtual são traduzidos para One, Two, etc.
- Cliques suspensos são cancelados em desativação rápida; comandos de liberação são enviados.
- Click TP PL acompanha também respawns de jogadores já existentes e limpa suas conexões.
- Corrigidos padrões booleanos que podiam resultar em nil.
- Dropdowns principais ganharam contratos Get/Set/Validate.
- Foi removida a segunda definição que substituía GroupObj:Input.
- Foram removidas funções e referências antigas sem uso.
- Estado/tamanho do menu foram alinhados entre botão móvel e atalho.

### Configurações

- 53 controles persistidos, incluindo listas, tamanho de nomes, alvo de clique, perfil, alvo/time de TP.
- Atalhos são salvos separadamente no mesmo esquema.
- Tipos, limites e algumas opções são validados antes da aplicação.
- Os formatos antigos continuam aceitos, incluindo o booleano antigo de nomes do ESP.
- Configuração tem versão de esquema, backup e verificação de escrita.
- JSON principal ilegível pode recuperar a cópia anterior.
- Falha de Get impede salvamento incompleto.
- Falha de Set devolve erro e tenta restaurar o estado anterior.
- A interface deixa de anunciar sucesso completo em aplicação com falhas.

Não há garantia de atomicidade para todas as APIs de executor. O backup e a verificação reduzem a possibilidade de perda, sem substituir essa garantia inexistente.

### Código remoto

A animação remota foi removida. O principal não contém HttpGet nem baixa módulos para iniciar.

A reexecução após teleporte usa conteúdo de **ShiKopo/ShiKopo.lua no espaço de arquivos do executor**, quando a opção estiver ligada e as APIs necessárias existirem. Essa cópia deve ser mantida atualizada pelo usuário; alterar a pasta Downloads não a sincroniza.

Esta revisão está publicada na branch main de Zyntra074/ShiKopo. Comandos antigos que apontam para outros repositórios não garantem carregar esta revisão.

## Situação dos 26 achados da auditoria

| Achado | Tratamento nesta revisão |
|---|---|
| A01 — Execução remota mutável | Removida da abertura e substituída por cópia local explícita na reexecução |
| A02 — Falha sem Drawing | Contratos completos, inicialização coberta e switch revertido em erro |
| A03 — Gestão global de recursos | Runtime, limpeza, recuperação e reexecução cobertos |
| A04 — UnfreezeCamera inexistente | Removida a chamada |
| A05 — Escopo das variáveis de alvo | Corrigido e testado |
| A06 — Colisões não restauradas | Valores anteriores guardados/restaurados |
| A07 — Sucesso parcial oculto | Erros detectados e propagados; rollback de carga |
| A08 — Persistência incompleta | Incluídos atalhos, listas e demais estados citados |
| A09 — Tipos de bind | Normalização e consultas de teclado/mouse unificadas |
| A10 — Respawn sem cancelamento | Geração/personagem/destino estável e teste de cancelamento |
| A11 — Esquema e recuperação | Esquema 2, validação, backup e rollback; sem promessa de atomicidade |
| A12 — Consultas repetidas | Caches, orçamento e filtro de FOV anterior |
| A13 — Hitbox por quadro | Atualização limitada, comparação e referências fracas |
| A14 — Varredura de mapa | Consulta espacial limitada, cache, cancelamento e orçamento |
| A15 — Objetos do ESP | Inventário alocado sob demanda e com alcance |
| A16 — Listeners do TP | Acompanhamento de personagens existentes/novos e limpeza |
| A17 — Tarefas visuais | Trabalho sob demanda, decoração opcional e conclusão sem acúmulo |
| A18 — Foco/captura de entrada | Guardas e normalização; sem teste de dispositivos físicos |
| A19 — UI móvel | Estado e dimensão corrigidos; validação física em dispositivos não realizada |
| A20 — Duplicidades/globais | Redefinição e globais acidentais corrigidas; sobras removidas |
| A21 — Teste só do simulador | Adicionados 52 cenários com o principal integral |
| A22 — Validador textual | Compilador Luau nativo, sem reescrever o fonte |
| A23 — Simulador insuficiente | Extensão determinística, serviços e captura de erros; não replica o cliente inteiro |
| A24 — Documentação contraditória | README, PROJECT e TEST_INFRA atualizados |
| A25 — Reprodutibilidade | Dependência fixada, instalador de Luau com hash e runner completo; sem CI remota executada |
| A26 — Origem/licença | Incertezas documentadas; não foi inventada licença nem confirmada autoria/origem |

A distribuição segue em um arquivo por escolha de compatibilidade. A documentação não afirma mais que existem modules/ e ui/.

## Testes e evidências

Ambiente: Python 3.12.14, Lupa 2.8 e Luau 0.744 oficial.

| Suíte | Resultado |
|---|---:|
| Smoke | 18/18 |
| Challenger M1 | 36/36 |
| Challenger JSON/VFS/Drawing | 20/20 |
| Challenger profundo | 10/10 |
| Regressões sintáticas | 7/7 |
| Integração do hub completo | 52/52 |
| Total de casos | **143/143** |
| Compilação nativa | **4/4 fontes Lua** |

Há testes de falha de serviço, ausência de Drawing, 50 alternâncias, troca rápida de estado, cancelamento de mapa/respawn/clique, roundtrip/rollback/backup de configuração, frequência em 144 Hz, 45 segundos de decoração e 50 reconstruções de favoritos.

Na entrega original, os logs e contadores foram guardados localmente em:

**C:\Users\Ekon\Downloads\ShiKopo_Correcoes_2026-10-25**

- benchmark.json;
- testes_finais/results.json;
- testes_finais/integration.log;
- demais logs das suítes;
- diff do principal e manifesto de integridade.

Para esta publicação, os testes e o benchmark foram reexecutados. Seus resultados atuais estão em [reports/2026-10-25/](reports/2026-10-25/), com logs, contadores e manifesto dos arquivos publicados. A cópia original e as ferramentas intermediárias continuam no arquivo local e não são dependências da distribuição.

A análise estática adicional não encontrou globais acidentais fora dos nomes esperados do Roblox/executor. O analisador Luau isolado não possui os tipos Roblox: seus diagnósticos de tipos/serviços não foram apresentados como validação tipada completa.

## Como testar no seu uso

1. Reconecte ao jogo para remover a instância antiga.
2. Carregue o ShiKopo.lua atualizado desta pasta.
3. Teste primeiro com tudo desligado.
4. Em Configs → Desempenho, compare Econômico e Equilibrado.
5. Ligue os recursos que utiliza, um por vez. Inventário e terreno têm orçamentos próprios.
6. Se precisar identificar a função mais pesada, ative “Medir custo das funções” e use “Mostrar diagnóstico”.

Essa sequência distingue custo do HUB ocioso de custo dos recursos ativos. O relatório não promete um número de FPS sem medição no cliente.

## Referências técnicas

A separação de tarefas do render segue [Roblox Task Scheduler](https://create.roblox.com/docs/performance-optimization/microprofiler/task-scheduler). A consulta de estruturas usa a API [WorldRoot:GetPartBoundsInRadius](https://create.roblox.com/docs/reference/engine/classes/WorldRoot#GetPartBoundsInRadius). A ferramenta de validação vem do [Luau oficial, versão 0.744](https://github.com/luau-lang/luau/releases/tag/0.744).

