# Changelog

## Publicação completa — 25/10/2026

- Recuperados e publicados os 13 arquivos da suíte de testes que faltavam no GitHub.
- Reexecutados os 143 casos e a compilação nativa dos quatro fontes Lua.
- Publicadas evidências e comparação de contadores em reports/2026-10-25/.
- Corrigidos o repositório de destino e o fluxo de manutenção em AGENTS.md e .agents/rules/.
- GitHub definido pelo proprietário como fonte oficial das próximas alterações.
- O conteúdo do script já publicado é idêntico ao das duas cópias locais recebidas.

## 2.1.0 — 25/10/2026

- Corrigidas inicialização sem Drawing, chamada inexistente ao desligar Cursor Aim e variáveis de alvo com escopo errado.
- Criados runtime compartilhado, encerramento central e recuperação de falha na inicialização.
- Recursos passam a conectar atualizações somente enquanto necessários.
- Adicionados perfis Econômico, Equilibrado e Alta atualização, medição opcional e diagnóstico.
- Removida execução remota da animação inicial; reexecução após teleporte usa cópia local explícita.
- Implementados cache de jogadores/amizade, filtro de FOV antes de raycast e aquisição de alvo em frequência separada.
- Hitbox evita reescritas iguais, reduz frequência e preserva/restaura propriedades.
- TP restaura colisões e respawn cancela tarefas de personagem/estado anteriores.
- ESP aloca inventário sob demanda e atualiza sua lista em intervalo próprio.
- Minimapa usa consulta espacial limitada, orçamento de frames, cache e cancelamento.
- Corrigidos restauração do Shift Lock, entrada de teclado/mouse, liberação de cliques e dígitos do teclado virtual.
- Persistência ampliada para 53 controles, com atalhos, listas, tamanho de nomes e alvo do Auto Click.
- Adicionados validação, backup, recuperação e rollback de configurações; falhas deixam de ser anunciadas como sucesso completo.
- Corrigidos métodos ausentes em dropdowns e eliminação da redefinição de Input.
- Corrigida gestão de listeners no Click TP PL, favoritos, eventos de término de entrada e conclusão de tweens.
- Neve desligada por padrão, opcional e limitada.
- Validação de sintaxe usa compilador Luau nativo; ampliada suíte para 143 casos.
- Documentação atualizada para a arquitetura efetivamente entregue.

As correções foram feitas inicialmente em entrega local e depois publicadas em Zyntra074/ShiKopo. Não houve medição de ganho de FPS no Roblox.

