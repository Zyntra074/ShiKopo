# Evidências da publicação — 25/10/2026

Revisão DreeZy-HUB 2.1.0 publicada em Zyntra074/ShiKopo.

## Verificações realizadas

- As duas cópias locais corrigidas foram comparadas e possuem o mesmo SHA-256.
- O conteúdo integral de RespawnHUD.lua retornado pelo GitHub antes desta publicação é idêntico ao da cópia local validada. O script principal não recebeu alterações funcionais nesta publicação.
- Os 23 arquivos listados no manifesto da entrega original foram conferidos contra seus hashes antes da preparação.
- Reexecutados 143 casos: smoke 18, challenger M1 36, probe 20, deep 10, regressões sintáticas 7 e integração 52. Todas as seis suítes terminaram com código zero.
- Os quatro fontes Lua passaram pelo compilador Luau nativo.
- Reexecutado o benchmark determinístico de 10 segundos a 60 quadros/s, comparando a cópia original com a revisão corrigida. Os cenários reproduziram os contadores registrados no relatório.

Ambiente de validação: Windows, Python 3.12.14, Lupa 2.8 e Luau 0.744. A suíte usou simulação com rede bloqueada; não houve execução no cliente Roblox nem medição de FPS real.

## Arquivos

- `results.json`: resultado e duração das seis suítes desta revalidação.
- `*.log`: saída das suítes, incluindo os quatro fontes compilados e os 52 cenários de integração.
- `benchmark.json`: contadores da comparação reproduzida.
- `manifest.json`: hashes SHA-256 dos arquivos desta entrega, exceto o próprio manifesto.

O manifesto original da entrega local registrava publicação externa como falsa. Essa informação descreve a entrega anterior, e não o estado após esta publicação. Arquivos intermediários, executáveis, ambiente Python e cópia original não fazem parte da distribuição.

## Identificação das versões comparadas

SHA-256 da cópia original: `49e72e0146692b36bc06d15fab97425331087e19e1cc3bc1b551b53c17d6dbca`.

SHA-256 do arquivo corrigido usado nos testes: `0146472c127215d3da72fe50f35ecdaa42633ed3aa37ef6a67cb051dcb0edc92`.

Para reproduzir os testes da versão publicada, siga `TEST_INFRA.md`. Para repetir a comparação antes/depois, `tests/benchmark_hub.py` também requer a cópia original identificada acima, preservada no arquivo local do proprietário.
