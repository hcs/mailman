INSERT INTO "acceptablealias" VALUES(1,'foo@example.com',1);
INSERT INTO "acceptablealias" VALUES(2,'bar@example.com',1);

INSERT INTO "address" VALUES(
    1,'anne@example.com',NULL,'Anne Person',
    '2012-04-19 00:52:24.826432','2012-04-19 00:49:42.373769',1,2);
INSERT INTO "address" VALUES(
    2,'bart@example.com',NULL,'Bart Person',
    '2012-04-19 00:53:25.878800','2012-04-19 00:49:52.882050',2,4);

INSERT INTO "domain" VALUES(
    1,'example.com','http://example.com',NULL,'postmaster@example.com');

INSERT INTO "mailinglist" VALUES(
    -- id,list_name,mail_host,include_list_post_header,include_rfc2369_headers
    1,'test','example.com',1,1,
    -- created_at,admin_member_chunksize,next_request_id,next_digest_number
    '2012-04-19 00:46:13.173844',30,1,1,
    -- digest_last_sent_at,volume,last_post_at,accept_these_nonmembers
    NULL,1,NULL,X'80025D71012E',
    -- acceptable_aliases_id,admin_immed_notify,admin_notify_mchanges
    NULL,1,0,
    -- administrivia,advertised,anonymous_list,archive,archive_private
    1,1,0,1,0,
    -- archive_volume_frequency
    1,
    --autorespond_owner,autoresponse_owner_text
    0,'',
    -- autorespond_postings,autoresponse_postings_text
    0,'',
    -- autorespond_requests,authoresponse_requests_text
    0,'',
    -- autoresponse_grace_period
    '90 days, 0:00:00',
    -- forward_unrecognized_bounces_to,process_bounces
    1,1,
    -- bounce_info_stale_after,bounce_matching_headers
    '7 days, 0:00:00','
# Lines that *start* with a ''#'' are comments.
to: friend@public.com
message-id: relay.comanche.denmark.eu
from: list@listme.com
from: .*@uplinkpro.com
',
    -- bounce_notify_owner_on_disable,bounce_notify_owner_on_removal
    1,1,
    -- bounce_score_threshold,bounce_you_are_disabled_warnings
    5,3,
    -- bounce_you_are_disabled_warnings_interval
    '7 days, 0:00:00',
    -- filter_action,filter_content,collapse_alternatives
    2,0,1,
    -- convert_html_to_plaintext,default_member_action,default_nonmember_action
    0,4,0,
    -- description
    '',
    -- digest_footer_uri
    'mailman:///$listname/$language/footer-generic.txt',
    -- digest_header_uri
    NULL,
    -- digest_is_default,digest_send_periodic,digest_size_threshold
    0,1,30.0,
    -- digest_volume_frequency,digestable,discard_these_nonmembers
    1,1,X'80025D71012E',
    -- emergency,encode_ascii_prefixes,first_strip_reply_to
    0,0,0,
    -- footer_uri
    'mailman:///$listname/$language/footer-generic.txt',
    -- forward_auto_discards,gateway_to_mail,gateway_to_news
    1,0,0,
    -- generic_nonmember_action,goodby_message_uri
    1,'',
    -- header_matches,header_uri,hold_these_nonmembers,info,linked_newsgroup
    X'80025D71012E',NULL,X'80025D71012E','','',
    -- max_days_to_hold,max_message_size,max_num_recipients
    0,40,10,
    -- member_moderation_notice,mime_is_default_digest,moderator_password
    '',0,NULL,
    -- new_member_options,news_moderation,news_prefix_subject_too
    256,0,1,
    -- nntp_host,nondigestable,nonmember_rejection_notice,obscure_addresses
    '',1,'',1,
    -- owner_chain,owner_pipeline,personalize,post_id
    'default-owner-chain','default-owner-pipeline',0,1,
    -- posting_chain,posting_pipeline,preferred_language,private_roster
    'default-posting-chain','default-posting-pipeline','en',1,
    -- display_name,reject_these_nonmembers
    'Test',X'80025D71012E',
    -- reply_goes_to_list,reply_to_address
    0,'',
    -- require_explicit_destination,respond_to_post_requests
    1,1,
    -- scrub_nondigest,send_goodbye_message,send_reminders,send_welcome_message
    0,1,1,1,
    -- subject_prefix,subscribe_auto_approval
    '[Test] ',X'80025D71012E',
    -- subscribe_policy,topics,topics_bodylines_limit,topics_enabled
    1,X'80025D71012E',5,0,
    -- unsubscribe_policy,welcome_message_uri
    0,'mailman:///welcome.txt');

INSERT INTO "member" VALUES(
    1,'d1243f4d-e604-4f6b-af52-98d0a7bce0f1',1,'test@example.com',4,NULL,5,1);
INSERT INTO "member" VALUES(
    2,'dccc3851-fdfb-4afa-90cf-bdcbf80ad0fd',2,'test@example.com',3,NULL,6,1);
INSERT INTO "member" VALUES(
    3,'479be431-45f2-473d-bc3c-7eac614030ac',3,'test@example.com',3,NULL,7,2);
INSERT INTO "member" VALUES(
    4,'e2dc604c-d93a-4b91-b5a8-749e3caade36',1,'test@example.com',4,NULL,8,2);

INSERT INTO "preferences" VALUES(1,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "preferences" VALUES(2,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "preferences" VALUES(3,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "preferences" VALUES(4,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "preferences" VALUES(5,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "preferences" VALUES(6,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "preferences" VALUES(7,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "preferences" VALUES(8,NULL,NULL,NULL,NULL,NULL,NULL,NULL);

INSERT INTO "user" VALUES(
    1,'Anne Person',NULL,'0adf3caa-6f26-46f8-a11d-5256c8148592',
    '2012-04-19 00:49:42.370493',1,1);
INSERT INTO "user" VALUES(
    2,'Bart Person',NULL,'63f5d1a2-e533-4055-afe4-475dec3b1163',
    '2012-04-19 00:49:52.868746',2,3);

INSERT INTO "uid" VALUES(1,'8bf9a615-f23e-4980-b7d1-90ac0203c66f');
INSERT INTO "uid" VALUES(2,'0adf3caa-6f26-46f8-a11d-5256c8148592');
INSERT INTO "uid" VALUES(3,'63f5d1a2-e533-4055-afe4-475dec3b1163');
INSERT INTO "uid" VALUES(4,'d1243f4d-e604-4f6b-af52-98d0a7bce0f1');
INSERT INTO "uid" VALUES(5,'dccc3851-fdfb-4afa-90cf-bdcbf80ad0fd');
INSERT INTO "uid" VALUES(6,'479be431-45f2-473d-bc3c-7eac614030ac');
INSERT INTO "uid" VALUES(7,'e2dc604c-d93a-4b91-b5a8-749e3caade36');
