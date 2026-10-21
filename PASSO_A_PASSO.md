# Etapa 1 — Cadastros: instalação e testes

Os nomes exatos dos menus do Supabase e do Streamlit podem mudar um pouco com o tempo.
Se algum nome não bater, procure o item mais parecido.

## Antes de começar
- Um e-mail que **continue sendo da empresa** (não pessoal). Ele será o dono das contas.
- Uma conta no **GitHub** (para guardar o código) e uma no **Streamlit Community Cloud** (para publicar), ambas gratuitas.
  Eu ainda não confirmei as regras atuais dessa hospedagem gratuita; confira ao criar a conta.

## Parte 1 — Banco de dados (Supabase)
1. Crie uma conta em supabase.com e um **projeto novo**. Anote a **senha do banco** em local seguro.
   Se puder escolher a região, escolha a mais próxima do Brasil (São Paulo).
2. No projeto, abra o **SQL Editor**, cole **todo** o conteúdo de `supabase/001_etapa1_cadastros.sql` e clique em **Run**.
   Rode **uma vez só**. Se aparecer erro, copie a mensagem e me envie.
3. Em **Authentication → Users**, crie os 4 usuários (**Add user**), com e-mail e senha, marcando a opção de confirmar o e-mail automaticamente:
   Roberto Avelino, José Maciel, Julya Lima e John Kelvyn.
4. Ainda em Authentication, nas configurações de login, **desligue a opção de novos cadastros** ("Allow new users to sign up").
   Assim só você cria usuários.
5. Abra `supabase/002_primeiro_administrador.sql`, troque o e-mail pelo do John Kelvyn, rode no SQL Editor e confira que aparece 1 linha com `admin` e `true`.
6. Em **Project Settings → API**, anote a **Project URL** e a chave **anon / public**.
   **Nunca use nem divulgue a chave `service_role`.**

## Parte 2 — Publicar a aplicação
1. No GitHub, crie um repositório **privado** e envie **todos** os arquivos desta pasta (exceto `.streamlit/secrets.toml`, se existir).
2. No Streamlit Community Cloud, clique em **New app**, escolha o repositório, o arquivo principal `app.py` e, em **Advanced settings → Secrets**, cole:
   ```
   SUPABASE_URL = "a Project URL"
   SUPABASE_ANON_KEY = "a chave anon"
   ```
3. Publique. O endereço do app funciona no computador e no celular.

## Parte 3 — Primeiro uso
1. Entre com o e-mail e a senha do John.
2. Menu **Usuários**: para cada um dos outros 3, **ative**, preencha o nome e a função (Roberto e José: Encarregado; Julya: Técnica) e deixe o perfil como **Operador**.
3. Menu **Famílias e Subtipos**: as 7 famílias já vêm cadastradas (os códigos de 3 letras são uma sugestão minha; confirme ou me diga o que mudar). Cadastre os subtipos reais.

## Parte 4 — Testes da Etapa 1 (marque cada um)
- [ ] Cadastrar 20 materiais reais, incluindo: um prego (unidade kg), uma tinta (unidade L), uma escora, uma chapa (reutilizável) e um item alugado (com locador).
- [ ] Conferir que os códigos saíram no formato `FAM-SUB-0001`, `FAM-SUB-0002`...
- [ ] Tentar cadastrar um material alugado **sem** locador: deve ser recusado.
- [ ] Cadastrar 3 obras e conferir as datas no formato DD/MM/AAAA e os valores em R$.
- [ ] Entrar com um Operador: ele deve **ver** os cadastros e **não** conseguir criar ou editar.
- [ ] Desativar um material: ele some da lista até marcar "Mostrar inativos" e **não** pode ser excluído.
- [ ] Cadastrar uma família com código repetido: deve ser recusado.
- [ ] Menu **Backup**: gerar o arquivo, baixar e abrir as planilhas.
- [ ] Anotar tudo que ficou estranho, confuso ou faltando.

## Cuidados
- Se o app ficar parado por um tempo, a hospedagem gratuita pode "dormir"; o primeiro acesso demora mais.
- No Supabase gratuito, o projeto pausa após cerca de 1 semana sem uso (por exemplo, em recesso). Os dados são mantidos, mas é preciso reativá-lo no painel.
- Faça o **backup toda semana** e antes de mudanças grandes. Teste abrir o arquivo.
- Cada usuário precisa fazer login de novo se recarregar a página.
