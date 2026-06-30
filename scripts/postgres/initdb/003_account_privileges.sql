-- 관리자 계정으로 scene_story_agent DB에 접속한 뒤 실행한다.
-- 로컬 개발 계정 기준: scene_story_agent / scene_story_agent

do $$
declare
    can_manage_roles boolean;
begin
    select rolsuper or rolcreaterole
    into can_manage_roles
    from pg_roles
    where rolname = current_user;

    if not exists (
        select 1
        from pg_roles
        where rolname = 'scene_story_agent'
    ) then
        if not can_manage_roles then
            raise exception 'scene_story_agent role does not exist. Run this file with a role that can create roles.';
        end if;

        create role scene_story_agent login password 'scene_story_agent';
    elsif can_manage_roles then
        alter role scene_story_agent with login password 'scene_story_agent';
    end if;
end $$;

alter database scene_story_agent owner to scene_story_agent;
grant all privileges on database scene_story_agent to scene_story_agent;

alter schema public owner to scene_story_agent;
grant usage, create on schema public to scene_story_agent;

do $$
declare
    target_object record;
    object_type text;
begin
    for target_object in
        select c.relkind, n.nspname, c.relname
        from pg_class c
        join pg_namespace n on n.oid = c.relnamespace
        where n.nspname = 'public'
          and c.relkind in ('r', 'p', 'v', 'm', 'S', 'f')
        order by c.relkind, c.relname
    loop
        object_type := case target_object.relkind
            when 'r' then 'table'
            when 'p' then 'table'
            when 'v' then 'view'
            when 'm' then 'materialized view'
            when 'S' then 'sequence'
            when 'f' then 'foreign table'
        end;

        execute format(
            'alter %s %I.%I owner to scene_story_agent',
            object_type,
            target_object.nspname,
            target_object.relname
        );
    end loop;
end $$;

grant select, insert, update, delete on all tables in schema public
    to scene_story_agent;

grant usage, select, update on all sequences in schema public
    to scene_story_agent;

grant execute on all functions in schema public
    to scene_story_agent;

alter default privileges in schema public
    grant select, insert, update, delete on tables
    to scene_story_agent;

alter default privileges in schema public
    grant usage, select, update on sequences
    to scene_story_agent;

alter default privileges in schema public
    grant execute on functions
    to scene_story_agent;
