# DEPLOY — HuggingFace LLaMA (MANDATORY) — Guia Completo

Este repositório foi configurado para usar **LLaMA 3.1 8B Instruct via HuggingFace Inference API** como o **motor OBRIGATÓRIO** de geração de conteúdo.
**Nenhuma chave OpenAI será aceita.**

## 1) Criar conta e gerar token HuggingFace (OBRIGATÓRIO)
1. Acesse https://huggingface.co e crie conta gratuita.
2. Vá em: https://huggingface.co/settings/tokens
3. Clique em "New token" e gere um token (role: `read`).
4. No GitHub, vá para: Settings → Secrets → Actions → New repository secret
   - Nome: `HUGGINGFACE_API_KEY`
   - Valor: cole seu token HF

**Sem esse token o workflow irá falhar intencionalmente.**

## 2) Atualizar config.json
- `domain`: seu domínio (ex: https://meusitefinanceiro.com)
- `cloudflare_beacon_token`: token Cloudflare Web Analytics (opcional, recomendado)
- `huggingface_model`: por padrão meta-llama/Llama-3.1-8B-Instruct (pode ajustar)

## 3) Subir repositório e executar workflow
- Faça commit/push de todos os arquivos para o branch `main`.
- Vá em GitHub → Actions → execute o workflow manualmente (workflow_dispatch) para testar.
- O workflow verifica que `HUGGINGFACE_API_KEY` existe, coleta tendências, gera 2 artigos via HuggingFace, gera site estático e publica no GitHub Pages.

## 4) Monitoramento & logs
- Arquivo `generation.log` registra todas as gerações e falhas.
- GitHub Actions mostra logs passo a passo.
- Notificações via Telegram (opcional): adicione `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` em Secrets para receber resultado (success/failure).

## 5) Teste local
- Exporte token localmente:
  ```bash
  export HUGGINGFACE_API_KEY="seu_token_aqui"
  pip install -r requirements.txt
  python scripts/collect_trending.py
  python scripts/generate_article.py --count 2
  python scripts/site_generator.py
  ```
- Verifique `content/posts/` e `site/output/`

## 6) Observações sobre gratuidade
- HuggingFace Inference API free tier supports light usage; 2 artigos por dia is well within typical free usage constraints for community models.
- Caso queira mais performance/resiliência, considere creating a serverless endpoint in HF (optional).

## 7) Checklist final
- [ ] Adicionar `HUGGINGFACE_API_KEY` (obrigatório)
- [ ] Atualizar `config.json` com `domain`
- [ ] Habilitar Pages / Deploy
- [ ] Testar workflow manualmente

Pronto — após isso o site ficará em produção usando exclusivamente LLaMA via HuggingFace (gratuito).
