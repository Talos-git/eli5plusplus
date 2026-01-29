# eli5plusplus
## Static Web + OpenRouter (Supabase Edge)

This repo now includes a static TypeScript frontend under `web/` and a Supabase Edge Function that proxies OpenRouter calls.

### Frontend setup

1. Install dependencies inside `web/`:
   ```bash
   cd web
   npm install
   ```
2. Provide the Edge Function URL as a Vite env var (e.g., in `web/.env.local`):
   ```bash
   VITE_OPENROUTER_FUNCTION_URL=https://<your-project>.functions.supabase.co/openrouter-explain
   ```
3. Run the dev server:
   ```bash
   npm run dev
   ```

### Supabase Edge Function setup

1. Create an Edge Function named `openrouter-explain` using the files in `supabase/functions/openrouter-explain/`.
2. Set the required secret:
   ```bash
   supabase secrets set OPENROUTER_API_KEY=your_openrouter_api_key
   ```
3. Optional: override the default model:
   ```bash
   supabase secrets set OPENROUTER_MODEL=openai/gpt-4o-mini
   ```

The frontend will call the Edge Function directly so the OpenRouter API key never ships to the browser.
