-- Rodar DEPOIS de criar seu usuário em Authentication > Users.
-- Troque o e-mail abaixo pelo e-mail do administrador (John Kelvyn).
update public.perfis
   set perfil = 'admin', ativo = true, nome = 'John Kelvyn', funcao = 'Técnico'
 where id = (select id from auth.users where email = 'TROQUE-PELO-SEU-EMAIL@exemplo.com');

-- Confira: deve aparecer 1 linha com perfil = admin e ativo = true.
select nome, perfil, ativo from public.perfis;
