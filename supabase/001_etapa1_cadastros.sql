-- =====================================================================
-- ETAPA 1 - CADASTROS (Sistema de Estoque de Escoramento)
-- Rodar UMA vez, no SQL Editor do Supabase, em um projeto novo.
-- =====================================================================

-- ---------- Funções auxiliares ----------
create or replace function public.set_atualizado_em()
returns trigger language plpgsql as $$
begin
  new.atualizado_em := now();
  return new;
end $$;

-- ---------- Usuários (perfis) ----------
create table public.perfis (
  id uuid primary key references auth.users(id),
  nome text not null,
  funcao text,
  perfil text not null default 'operador' check (perfil in ('admin','operador')),
  ativo boolean not null default false,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

create or replace function public.eh_usuario_ativo()
returns boolean language sql security definer stable set search_path = public as $$
  select exists (select 1 from public.perfis where id = auth.uid() and ativo);
$$;

create or replace function public.eh_admin()
returns boolean language sql security definer stable set search_path = public as $$
  select exists (select 1 from public.perfis where id = auth.uid() and ativo and perfil = 'admin');
$$;

-- Todo usuário criado no Supabase ganha um perfil INATIVO (o admin ativa depois).
create or replace function public.novo_usuario()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.perfis (id, nome, ativo)
  values (new.id, coalesce(new.raw_user_meta_data->>'nome', split_part(new.email, '@', 1)), false);
  return new;
end $$;

create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.novo_usuario();

-- Impede ficar sem nenhum administrador ativo.
create or replace function public.proteger_ultimo_admin()
returns trigger language plpgsql as $$
begin
  if old.perfil = 'admin' and old.ativo and (new.perfil <> 'admin' or not new.ativo) then
    if not exists (select 1 from public.perfis where perfil = 'admin' and ativo and id <> old.id) then
      raise exception 'Deve existir pelo menos um administrador ativo.';
    end if;
  end if;
  return new;
end $$;

create trigger trg_proteger_ultimo_admin before update on public.perfis
for each row execute function public.proteger_ultimo_admin();
create trigger trg_atualizado_em before update on public.perfis
for each row execute function public.set_atualizado_em();

-- ---------- Famílias e subtipos (base do código FAM-SUB-NNNN) ----------
create table public.familias (
  id bigint generated always as identity primary key,
  codigo text not null unique check (codigo ~ '^[A-Z]{3}$'),
  nome text not null,
  ativo boolean not null default true,
  criado_em timestamptz not null default now(),
  criado_por uuid default auth.uid(),
  atualizado_em timestamptz not null default now()
);

create table public.subtipos (
  id bigint generated always as identity primary key,
  familia_id bigint not null references public.familias(id),
  codigo text not null check (codigo ~ '^[A-Z]{3}$'),
  nome text not null,
  ultimo_numero integer not null default 0,
  ativo boolean not null default true,
  criado_em timestamptz not null default now(),
  criado_por uuid default auth.uid(),
  atualizado_em timestamptz not null default now(),
  unique (familia_id, codigo)
);

-- ---------- Demais cadastros ----------
create table public.estados_conservacao (
  id bigint generated always as identity primary key,
  nome text not null unique,
  ordem integer not null,
  ativo boolean not null default true,
  criado_em timestamptz not null default now(),
  criado_por uuid default auth.uid(),
  atualizado_em timestamptz not null default now()
);

create table public.depositos (
  id bigint generated always as identity primary key,
  nome text not null unique,
  endereco text,
  ativo boolean not null default true,
  criado_em timestamptz not null default now(),
  criado_por uuid default auth.uid(),
  atualizado_em timestamptz not null default now()
);

create table public.fornecedores (
  id bigint generated always as identity primary key,
  nome text not null unique,
  tipo text not null default 'fornecedor' check (tipo in ('fornecedor','locador','ambos')),
  contato text,
  ativo boolean not null default true,
  criado_em timestamptz not null default now(),
  criado_por uuid default auth.uid(),
  atualizado_em timestamptz not null default now()
);

create table public.obras (
  id bigint generated always as identity primary key,
  nome text not null unique,
  contrato text,
  endereco text,
  situacao text not null default 'planejada' check (situacao in ('planejada','ativa','concluida')),
  data_inicio_prevista date,
  data_fim_prevista date,
  ativo boolean not null default true,
  criado_em timestamptz not null default now(),
  criado_por uuid default auth.uid(),
  atualizado_em timestamptz not null default now(),
  check (data_fim_prevista is null or data_inicio_prevista is null or data_fim_prevista >= data_inicio_prevista)
);

-- ---------- Materiais ----------
create table public.materiais (
  id bigint generated always as identity primary key,
  codigo text not null unique,                       -- gerado automaticamente
  subtipo_id bigint not null references public.subtipos(id),
  descricao text not null,
  unidade text not null check (unidade in ('peça','kg','L')),
  peso_unitario_kg numeric(12,3) check (peso_unitario_kg is null or peso_unitario_kg >= 0),
  comprimento_m numeric(10,3) check (comprimento_m is null or comprimento_m >= 0),
  largura_m numeric(10,3) check (largura_m is null or largura_m >= 0),
  altura_m numeric(10,3) check (altura_m is null or altura_m >= 0),
  custo_unitario numeric(12,2) not null default 0 check (custo_unitario >= 0),   -- R$
  tipo text not null check (tipo in ('reutilizavel','consumivel')),
  propriedade text not null default 'proprio' check (propriedade in ('proprio','alugado')),
  fornecedor_id bigint references public.fornecedores(id),
  vida_util_meses numeric(6,1) check (vida_util_meses is null or vida_util_meses > 0),
  estoque_minimo numeric(12,3) not null default 0 check (estoque_minimo >= 0),
  observacoes text,
  ativo boolean not null default true,
  criado_em timestamptz not null default now(),
  criado_por uuid default auth.uid(),
  atualizado_em timestamptz not null default now(),
  check (propriedade = 'proprio' or fornecedor_id is not null)
);

-- Gera FAM-SUB-NNNN. O contador só aumenta: um código nunca é reaproveitado.
create or replace function public.gerar_codigo_material()
returns trigger language plpgsql security definer set search_path = public as $$
declare v_sub text; v_num integer; v_fid bigint; v_fam text;
begin
  update public.subtipos s set ultimo_numero = s.ultimo_numero + 1
   where s.id = new.subtipo_id
  returning s.codigo, s.ultimo_numero, s.familia_id into v_sub, v_num, v_fid;
  if not found then
    raise exception 'Subtipo inexistente.';
  end if;
  select codigo into v_fam from public.familias where id = v_fid;
  new.codigo := v_fam || '-' || v_sub || '-' || lpad(v_num::text, 4, '0');
  return new;
end $$;

create trigger trg_gerar_codigo before insert on public.materiais
for each row execute function public.gerar_codigo_material();

-- Código, família e subtipo não mudam depois de criados.
create or replace function public.travar_campos_estruturais()
returns trigger language plpgsql as $$
begin
  if new.codigo is distinct from old.codigo then
    raise exception 'O código não pode ser alterado.';
  end if;
  if tg_table_name = 'materiais' then
    if new.subtipo_id is distinct from old.subtipo_id then
      raise exception 'O subtipo do material não pode ser alterado.';
    end if;
  elsif tg_table_name = 'subtipos' then
    if new.familia_id is distinct from old.familia_id then
      raise exception 'A família do subtipo não pode ser alterada.';
    end if;
  end if;
  return new;
end $$;

create trigger trg_travar before update on public.familias
for each row execute function public.travar_campos_estruturais();
create trigger trg_travar before update on public.subtipos
for each row execute function public.travar_campos_estruturais();
create trigger trg_travar before update on public.materiais
for each row execute function public.travar_campos_estruturais();

-- ---------- Segurança (RLS) ----------
-- Leitura: usuário ativo. Cadastro/edição: só administrador. Exclusão: ninguém
-- (nada é apagado; usa-se "ativo = falso").
do $$
declare t text;
begin
  foreach t in array array['familias','subtipos','estados_conservacao','depositos',
                           'fornecedores','obras','materiais'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('create policy "leitura" on public.%I for select to authenticated using (public.eh_usuario_ativo())', t);
    execute format('create policy "inserir_admin" on public.%I for insert to authenticated with check (public.eh_admin())', t);
    execute format('create policy "alterar_admin" on public.%I for update to authenticated using (public.eh_admin()) with check (public.eh_admin())', t);
    execute format('create trigger trg_atualizado_em before update on public.%I for each row execute function public.set_atualizado_em()', t);
  end loop;
end $$;

alter table public.perfis enable row level security;
create policy "leitura" on public.perfis for select to authenticated
  using (public.eh_usuario_ativo() or id = auth.uid());
create policy "alterar_admin" on public.perfis for update to authenticated
  using (public.eh_admin()) with check (public.eh_admin());

revoke all on all tables in schema public from anon;

-- ---------- Dados iniciais ----------
insert into public.estados_conservacao (nome, ordem) values
  ('Novo',1), ('Bom',2), ('Regular',3), ('Precisa de reparo',4), ('Sucata',5);

insert into public.depositos (nome) values ('Galpão');

insert into public.familias (codigo, nome) values
  ('ESC','Escoramento'), ('CHP','Chapas'), ('SAR','Sarrafos'), ('PRG','Pregos'),
  ('AND','Andaimes'),    ('TIN','Tintas'), ('ALM','Materiais de almoxarife');
