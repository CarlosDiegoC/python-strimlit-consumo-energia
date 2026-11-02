# Dashboard de consumo de energia elétrica

Aplicação Streamlit para consulta do consumo de energia elétrica por período, região, UF, classe e tipo de consumidor.

## Executar

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Estrutura

- `app.py`: interface principal e integração dos módulos.
- `data/`: planilha de consumo e CSV da produção industrial.
- `charts/`: funções Plotly separadas por visão geral, consumo e região; layout comum.
- `services/data_loader.py`: leitura e padronização dos arquivos.
- `services/data_processing.py`: tratamento interno da base de consumo.
- `services/analytics.py`: agregações e métricas.
- `components/`: filtros e cartões de indicadores.
- `config/theme.py`: cores e identidade visual.

## Observações

- A série de consumo vai de janeiro de 2004 a julho de 2026; o ano de 2026 está incompleto.
- A série industrial vai de janeiro de 2002 a agosto de 2026; a comparação usa apenas meses em comum e normaliza ambas as séries em índice 100 no primeiro mês compartilhado.
- A comparação percentual entre UFs usa 2004 e 2025, exigindo 12 meses disponíveis em cada ano para a UF.