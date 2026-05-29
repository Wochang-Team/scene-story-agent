create table if not exists app_users (
    user_id uuid primary key default uuidv7(),
    auth_provider text not null,
    auth_subject text not null,
    email text,
    display_name text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    deleted_at timestamptz,
    unique (auth_provider, auth_subject)
);

create table if not exists records (
    record_id uuid primary key default uuidv7(),
    user_id uuid not null references app_users(user_id),
    memo text,
    emotion text,
    satisfaction_score smallint,
    happened_at timestamptz,
    status text not null default 'draft',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    deleted_at timestamptz,
    check (satisfaction_score is null or satisfaction_score between 1 and 5),
    check (status in ('draft', 'processing', 'ready', 'failed', 'deleted'))
);

create index if not exists idx_records_user_happened_at
    on records (user_id, happened_at desc);

create index if not exists idx_records_user_created_at
    on records (user_id, created_at desc);

create table if not exists record_assets (
    asset_id uuid primary key default uuidv7(),
    record_id uuid not null references records(record_id),
    asset_type text not null,
    storage_provider text not null,
    bucket_name text not null,
    object_key text not null,
    content_type text not null,
    byte_size bigint,
    width integer,
    height integer,
    duration_seconds integer,
    checksum_sha256 text,
    created_at timestamptz not null default now(),
    deleted_at timestamptz,
    unique (storage_provider, bucket_name, object_key),
    check (asset_type in ('photo', 'video', 'thumbnail'))
);

create table if not exists record_ai_interpretations (
    interpretation_id uuid primary key default uuidv7(),
    record_id uuid not null references records(record_id),
    provider text not null,
    model text not null,
    scene_type text,
    summary text,
    ocr_candidates jsonb,
    place_candidates jsonb,
    visit_time_candidates jsonb,
    menu_candidates jsonb,
    activity_candidates jsonb,
    amount_candidates jsonb,
    similar_record_candidates jsonb,
    revisit_candidates jsonb,
    timeline_candidates jsonb,
    tags jsonb,
    user_corrections jsonb,
    raw_response_ref jsonb,
    status text not null default 'pending',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    deleted_at timestamptz,
    check (status in ('pending', 'completed', 'failed', 'user_edited'))
);

alter table record_ai_interpretations
    add column if not exists deleted_at timestamptz;

alter table record_ai_interpretations
    add column if not exists visit_time_candidates jsonb,
    add column if not exists activity_candidates jsonb,
    add column if not exists similar_record_candidates jsonb,
    add column if not exists revisit_candidates jsonb,
    add column if not exists timeline_candidates jsonb;

create table if not exists record_embeddings (
    embedding_id uuid primary key default uuidv7(),
    record_id uuid not null references records(record_id),
    provider text not null,
    model text not null,
    dimension integer not null,
    embedding vector,
    input_snapshot jsonb not null,
    created_at timestamptz not null default now(),
    deleted_at timestamptz
);

create index if not exists idx_record_embeddings_record_created
    on record_embeddings (record_id, created_at desc);

create table if not exists record_relations (
    relation_id uuid primary key default uuidv7(),
    source_record_id uuid not null references records(record_id),
    target_record_id uuid not null references records(record_id),
    relation_type text not null,
    similarity_score numeric(6,5),
    decision_status text not null default 'suggested',
    reasons jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    check (source_record_id <> target_record_id),
    check (relation_type in (
        'similar_scene',
        'same_place_candidate',
        'similar_topic',
        'revisit_candidate',
        'timeline_candidate'
    )),
    check (decision_status in ('suggested', 'accepted', 'rejected', 'hidden')),
    unique (source_record_id, target_record_id, relation_type)
);

create index if not exists idx_record_relations_source
    on record_relations (source_record_id, decision_status, created_at desc);

create table if not exists timeline_candidates (
    timeline_candidate_id uuid primary key default uuidv7(),
    user_id uuid not null references app_users(user_id),
    record_id uuid not null references records(record_id),
    timeline_type text not null,
    grouping_key text not null,
    confidence_score numeric(6,5),
    reasons jsonb,
    created_at timestamptz not null default now(),
    check (timeline_type in ('time', 'place', 'scene_type', 'emotion', 'topic'))
);

create unique index if not exists uq_timeline_candidates_user_record_type_key
    on timeline_candidates (user_id, record_id, timeline_type, grouping_key);

create table if not exists processing_jobs (
    job_id uuid primary key default uuidv7(),
    record_id uuid not null references records(record_id),
    job_type text not null,
    status text not null default 'queued',
    attempt_count integer not null default 0,
    last_error_code text,
    last_error_message text,
    available_at timestamptz not null default now(),
    started_at timestamptz,
    finished_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    check (job_type in (
        'extract_ai_interpretation',
        'create_embedding',
        'find_related_records',
        'generate_timeline_candidates',
        'delete_record_artifacts'
    )),
    check (status in ('queued', 'running', 'succeeded', 'failed', 'retrying', 'canceled'))
);

create index if not exists idx_processing_jobs_record_type_status
    on processing_jobs (record_id, job_type, status);

create index if not exists idx_processing_jobs_available
    on processing_jobs (status, available_at, created_at);
