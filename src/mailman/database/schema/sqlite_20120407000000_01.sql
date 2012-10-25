-- THIS FILE CONTAINS THE SQLITE3 SCHEMA MIGRATION FROM
-- 3.0b1 TO 3.0b2
--
-- AFTER 3.0b2 IS RELEASED YOU MAY NOT EDIT THIS FILE.

-- For SQLite3 migration strategy, see
-- http://sqlite.org/faq.html#q11

-- REMOVALS from the mailinglist table.
-- REM archive
-- REM archive_private
-- REM archive_volume_frequency
-- REM include_list_post_header
-- REM news_moderation
-- REM news_prefix_subject_too
-- REM nntp_host
--
-- ADDS to the mailing list table.
-- ADD allow_list_posts
-- ADD archive_policy
-- ADD list_id
-- ADD newsgroup_moderation
-- ADD nntp_prefix_subject_too

-- LP: #971013
-- LP: #967238

-- REMOVALS from the member table.
-- REM mailing_list

-- ADDS to the member table.
-- ADD list_id

-- LP: #1024509


CREATE TABLE ml_backup(
    id INTEGER NOT NULL,
    -- List identity
    list_name TEXT,
    mail_host TEXT,
    allow_list_posts BOOLEAN,
    include_rfc2369_headers BOOLEAN,
    -- Attributes not directly modifiable via the web u/i
    created_at TIMESTAMP,
    admin_member_chunksize INTEGER,
    next_request_id INTEGER,
    next_digest_number INTEGER,
    digest_last_sent_at TIMESTAMP,
    volume INTEGER,
    last_post_at TIMESTAMP,
    accept_these_nonmembers BLOB,
    acceptable_aliases_id INTEGER,
    admin_immed_notify BOOLEAN,
    admin_notify_mchanges BOOLEAN,
    administrivia BOOLEAN,
    advertised BOOLEAN,
    anonymous_list BOOLEAN,
    -- Automatic responses.
    autorespond_owner INTEGER,
    autoresponse_owner_text TEXT,
    autorespond_postings INTEGER,
    autoresponse_postings_text TEXT,
    autorespond_requests INTEGER,
    autoresponse_request_text TEXT,
    autoresponse_grace_period TEXT,
    -- Bounces.
    forward_unrecognized_bounces_to INTEGER,
    process_bounces BOOLEAN,
    bounce_info_stale_after TEXT,
    bounce_matching_headers TEXT,
    bounce_notify_owner_on_disable BOOLEAN,
    bounce_notify_owner_on_removal BOOLEAN,
    bounce_score_threshold INTEGER,
    bounce_you_are_disabled_warnings INTEGER,
    bounce_you_are_disabled_warnings_interval TEXT,
    -- Content filtering.
    filter_action INTEGER,
    filter_content BOOLEAN,
    collapse_alternatives BOOLEAN,
    convert_html_to_plaintext BOOLEAN,
    default_member_action INTEGER,
    default_nonmember_action INTEGER,
    description TEXT,
    digest_footer_uri TEXT,
    digest_header_uri TEXT,
    digest_is_default BOOLEAN,
    digest_send_periodic BOOLEAN,
    digest_size_threshold FLOAT,
    digest_volume_frequency INTEGER,
    digestable BOOLEAN,
    discard_these_nonmembers BLOB,
    emergency BOOLEAN,
    encode_ascii_prefixes BOOLEAN,
    first_strip_reply_to BOOLEAN,
    footer_uri TEXT,
    forward_auto_discards BOOLEAN,
    gateway_to_mail BOOLEAN,
    gateway_to_news BOOLEAN,
    goodbye_message_uri TEXT,
    header_matches BLOB,
    header_uri TEXT,
    hold_these_nonmembers BLOB,
    info TEXT,
    linked_newsgroup TEXT,
    max_days_to_hold INTEGER,
    max_message_size INTEGER,
    max_num_recipients INTEGER,
    member_moderation_notice TEXT,
    mime_is_default_digest BOOLEAN,
    moderator_password TEXT,
    new_member_options INTEGER,
    nondigestable BOOLEAN,
    nonmember_rejection_notice TEXT,
    obscure_addresses BOOLEAN,
    owner_chain TEXT,
    owner_pipeline TEXT,
    personalize INTEGER,
    post_id INTEGER,
    posting_chain TEXT,
    posting_pipeline TEXT,
    preferred_language TEXT,
    private_roster BOOLEAN,
    display_name TEXT,
    reject_these_nonmembers BLOB,
    reply_goes_to_list INTEGER,
    reply_to_address TEXT,
    require_explicit_destination BOOLEAN,
    respond_to_post_requests BOOLEAN,
    scrub_nondigest BOOLEAN,
    send_goodbye_message BOOLEAN,
    send_reminders BOOLEAN,
    send_welcome_message BOOLEAN,
    subject_prefix TEXT,
    subscribe_auto_approval BLOB,
    subscribe_policy INTEGER,
    topics BLOB,
    topics_bodylines_limit INTEGER,
    topics_enabled BOOLEAN,
    unsubscribe_policy INTEGER,
    welcome_message_uri TEXT,
    PRIMARY KEY (id)
    );

INSERT INTO ml_backup SELECT
    id,
    -- List identity
    list_name,
    mail_host,
    include_list_post_header,
    include_rfc2369_headers,
    -- Attributes not directly modifiable via the web u/i
    created_at,
    admin_member_chunksize,
    next_request_id,
    next_digest_number,
    digest_last_sent_at,
    volume,
    last_post_at,
    accept_these_nonmembers,
    acceptable_aliases_id,
    admin_immed_notify,
    admin_notify_mchanges,
    administrivia,
    advertised,
    anonymous_list,
    -- Automatic responses.
    autorespond_owner,
    autoresponse_owner_text,
    autorespond_postings,
    autoresponse_postings_text,
    autorespond_requests,
    autoresponse_request_text,
    autoresponse_grace_period,
    -- Bounces.
    forward_unrecognized_bounces_to,
    process_bounces,
    bounce_info_stale_after,
    bounce_matching_headers,
    bounce_notify_owner_on_disable,
    bounce_notify_owner_on_removal,
    bounce_score_threshold,
    bounce_you_are_disabled_warnings,
    bounce_you_are_disabled_warnings_interval,
    -- Content filtering.
    filter_action,
    filter_content,
    collapse_alternatives,
    convert_html_to_plaintext,
    default_member_action,
    default_nonmember_action,
    description,
    digest_footer_uri,
    digest_header_uri,
    digest_is_default,
    digest_send_periodic,
    digest_size_threshold,
    digest_volume_frequency,
    digestable,
    discard_these_nonmembers,
    emergency,
    encode_ascii_prefixes,
    first_strip_reply_to,
    footer_uri,
    forward_auto_discards,
    gateway_to_mail,
    gateway_to_news,
    goodbye_message_uri,
    header_matches,
    header_uri,
    hold_these_nonmembers,
    info,
    linked_newsgroup,
    max_days_to_hold,
    max_message_size,
    max_num_recipients,
    member_moderation_notice,
    mime_is_default_digest,
    moderator_password,
    new_member_options,
    nondigestable,
    nonmember_rejection_notice,
    obscure_addresses,
    owner_chain,
    owner_pipeline,
    personalize,
    post_id,
    posting_chain,
    posting_pipeline,
    preferred_language,
    private_roster,
    display_name,
    reject_these_nonmembers,
    reply_goes_to_list,
    reply_to_address,
    require_explicit_destination,
    respond_to_post_requests,
    scrub_nondigest,
    send_goodbye_message,
    send_reminders,
    send_welcome_message,
    subject_prefix,
    subscribe_auto_approval,
    subscribe_policy,
    topics,
    topics_bodylines_limit,
    topics_enabled,
    unsubscribe_policy,
    welcome_message_uri
    FROM mailinglist;

CREATE TABLE mem_backup(
    id INTEGER NOT NULL,
    _member_id TEXT,
    role INTEGER,
    moderation_action INTEGER,
    address_id INTEGER,
    preferences_id INTEGER,
    user_id INTEGER,
    PRIMARY KEY (id)
    );

INSERT INTO mem_backup SELECT
    id,
    _member_id,
    role,
    moderation_action,
    address_id,
    preferences_id,
    user_id
    FROM member;
    

-- Add the new columns.  They'll get inserted at the Python layer.
ALTER TABLE ml_backup ADD COLUMN archive_policy INTEGER;
ALTER TABLE ml_backup ADD COLUMN list_id TEXT;
ALTER TABLE ml_backup ADD COLUMN nntp_prefix_subject_too INTEGER;
ALTER TABLE ml_backup ADD COLUMN newsgroup_moderation INTEGER;

ALTER TABLE mem_backup ADD COLUMN list_id TEXT;
