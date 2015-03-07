
-- Copyright @2015 by ruuxee.com, All rights reserved.
-- This is the script to show the database schema, in MySQL format.

-- NOTE Several rules ahead:
-- a. All strings (name, email, etc.) are stored as utf-8 format.
-- b. We don't save all data in MySQL. The database is for data that
--    does not change frequently, like basic user information. There are
--    a lot of data, which can be changed frequently, like vote/unvote,
--    follow/unfollow. We save them in redis. See below for more
--    details.

CREATE TABLE ruuxee_person_v1 (
    id INT NOT NULL AUTO_INCREMENT, -- Internal ID, used only in database
    visible_id CHAR(16),            -- Visible ID, used in public webpage
    anonymous_sha1 CHAR(40),        -- Used internally for anonymous post
    status INT,                     -- multiple user status (see below)
    name VARCHAR(80),               -- User name, like "Fuzhou Chen"
    readable_id VARCHAR(16),        -- Readable user ID, like "fuzhou.chen"
    email VARCHAR(320),             -- Email address
    password_sha1 CHAR(40),         -- SHA1 hash of user's password string
    signup_timestamp TIMESTAMP,     -- Signup timestamp
    avartar_url VARCHAR(256),       -- URL to avartar
    description VARCHAR(768),       -- 256 utf-8 Chinese characters.
    job         VARCHAR(96),        -- 32 utf-8 Chinese characters.
    company     VARCHAR(96),        -- 32 utf-8 Chinese characters.
    city        VARCHAR(48),        -- 16 utf-8 Chinese characters.
    country     VARCHAR(96)         -- 32 utf-8 Chinese characters.
    -- TODO There should be an ID here to identify the table that
    -- stores user's history, posts and timeline. However we don't set
    -- it here to avoid over design. It should be updated in the later
    -- version of table schema.
)

-- Enumerated user status
--     Registered = 1 = wait for email validation.
--     Verified   = 2 = Verification passed. Can access full feature.
--     Suspended  = 3 = User is suspended by admin. Can't login.
--     Deleted    = 4 = User is deleted. Can't login any more.

CREATE TABLE ruuxee_post_v1 (
    id INT NOT NULL AUTO_INCREMENT, -- Internal ID, used only in database
    visible_id CHAR(16),            -- Visible ID, used in public webpage
    status INT,                     -- Status of this post (see below)
    is_anonymous BOOLEAN,           -- Check if the post is boolean
    author_visible_id INT,          -- The user who writes the post
    topic_visible_id INT,           -- The topic that this post belongs to
    written_timestamp TIMESTAMP,    -- The time the post is written
    title VARCHAR(192),             -- 64 utf-8 Chinese characters
    content_html VARCHAR(30000)     -- 10000 utf-8 Chinese characters
    brief_text VARCHAR(300)         -- 300 utf-8 Chinese characters
)

-- Enumerated post status
--     Activated = 1 = Posted to public
--     Reviewing = 2 = Pending for review. Not visible in web site.
--     Suspended = 3 = Posted but put back for administrative reason.
--     Deleted   = 4 = Deleted. Not visible to public.

CREATE TABLE ruuxee_topic_v1 (
    id INT NOT NULL AUTO_INCREMENT, -- Internal ID, used only in database
    visible_id CHAR(16),            -- Visible ID, used in public webpage
    title VARCHAR(192),             -- 64 utf-8 Chinese characters
    description VARCHAR(768)        -- 256 utf-8 Chinese characters.
)
-- TODO There are still several items missing:
-- a. Define topic category and sub-category.
-- b. Define comments.

-- ==================== Part 2: Redis-cached data ===================

-- 1. Person's action history (TABLE_NAME_PERSON_ACTIONS)
--     type = list
--     name = "pa{person_visible_id}"
--     value = "{timestamp}:{action_id}:{target_visible_id}"

--     Values of action_id
--         PERSON_ACTION_CREATE_ACCOUNT = 'a'
--         PERSON_ACTION_DELETE_ACCOUNT = 'b'
--         PERSON_ACTION_UPDATE_ACCOUNT_INFO = 'c'
--         PERSON_ACTION_LOGIN = 'd'
--         PERSON_ACTION_LOGOUT = 'e'
--         PERSON_ACTION_FOLLOW_PERSON = 'f'
--         PERSON_ACTION_UNFOLLOW_PERSON = 'g'
--         PERSON_ACTION_FOLLOW_TOPIC = 'h'
--         PERSON_ACTION_UNFOLLOW_TOPIC = 'i'
--         PERSON_ACTION_UPVOTE_POST = 'j'
--         PERSON_ACTION_NEUTRALIZE_POST = 'k'
--         PERSON_ACTION_DOWNVOTE_POST = 'l'
--         PERSON_ACTION_ADD_POST = 'm'
--         PERSON_ACTION_EDIT_POST = 'n'
--         PERSON_ACTION_DELETE_POST = 'o'
--         PERSON_ACTION_ADD_COMMENT = 'p'
--         PERSON_ACTION_EDIT_COMMENT = 'q'
--         PERSON_ACTION_REMOVE_COMMENT = 'r'
--         PERSON_ACTION_ADD_TOPIC = 's'
--         PERSON_ACTION_EDIT_TOPIC = 't'
--         PERSON_ACTION_REMOVE_TOPIC = 'u'
--
-- TODO
-- *. We may not be able to fully identify the logout timestamp.
-- *. The format is incompatible with "add_category_to_topic" and
--    "remove_topic_from_category". May need special case.

-- 2. Post upvoted by person list (TABLE_NAME_POST_UPVOTE)
--     type = list
--     name = "pu{post_visible_id}"
--     value = "{person_visible_id}"

-- 3. Post downvoted by person list (TABLE_NAME_POST_DOWNVOTE)
--     type = list
--     name = "pd{post_visible_id}"
--     value = "{person_visible_id}"
--
-- 4. Person-follow-person list (TABLE_NAME_PERSON_FOLLOW_PERSON)
--     type = set
--     name = "pfp{person_visible_id}"
--     value = "{to_person_visible_id}"

-- 5. Person-follow-topic list (TABLE_NAME_PERSON_FOLLOW_TOPIC)
--     type = set
--     name = "pft{person_visible_id}"
--     value = "{to_topic_visible_id}"

-- 6. Person-followed-by-person list (TABLE_NAME_PERSON_FOLLOWED_BY_PERSON)
--     type = set
--     name = "pfbp{to_person_visible_id}"
--     value = "{from_person_visible_id}"

-- 7. Topic-followed-by-person list (TABLE_NAME_TOPIC_FOLLOWED_BY_PERSON)
--     type = set
--     name = "tfbp{to_person_visible_id}"
--     value = "{from_person_visible_id}"

-- 8. Person's timeline (from latest to earlest)
--     type = list
--     name = "pt{person_visible_id}"
--     value = {timestamp}:{action_id}:{from_person_visible_id}:{to_target_visible_id}
-- NOTE
--     This list is updated when a person add an action. A step looks
--     like below:
--
--         when person_11223344 do action_k on post_22334455:
--             for each_person_id in pfp11223344:
--                 pt{each_person_id}.prepend_list(timestamp,
--                                                 "k",11223344,22334455)
-- TO BE IMPLEMENTED:
-- 7. Person's login/logout status
--     type = set
--     name = "pls"
--     value = "{person_visible_id}"
--
-- 8. Person's login session list
--     type = set
--     name = "pls{person_visible_id}"
--     value = "{encrypted_session}:{expire_timestamp}:{source}:{platform}"

-- NOTE
-- a. We must assume multple login sessions from different browsers or
--    apps.

-- Values of source
--     * a: Unknown browser
--     * b: Official mobile app
--     * c: IE
--     * d: Safari
--     * e: Firefox
--     * f: Chrome
--     * g: Opera
-- Values of platform
--     * a: Unknown Platform
--     * b: Windows
--     * c: Mac
--     * d: Linux
--     * e: iOS
--     * f: Android
--     * g: Windows Phone

-- ============== Example: Possible actions ================
-- 1. When a person login (assume visible ID = 12345678)
--    a. LPUSH an item in pa12345678 list.
--    b. SADD 12345678 to pls set.
--    c. SADD session ID to pls12345678 list
--    d. LINDEX the first 30 items from pt12345678 list.
--    e. Use items from step d to render static page.
--    f. Encrypt "{session_id}:{expire_time}" and set in cookie.
--    f. Return page and cookie to browsers.
--    g. Browser uses Web APIs to get newer updates from pt12345678 list.

-- Step a to c make system know if this user logs on.
-- Step d to f can get initial page rendered from server side and return.

-- Part 4: Web pages and APIs
-- Web pages
--    GET http://www.ruuxee.com/person
--    GET http://www.ruuxee.com/person/<person_visible_id>
--    GET http://www.ruuxee.com/person/<person_readable_id>
--    GET http://www.ruuxee.com/post/<post_visible_id>
--
-- APIs
-- 1. GET http://www.ruuxee.com/api/web/v1/person_brief/<visible_id>
--   Purpose:
--       Get brief information of a person, shown in hovering info.
--   Return:
--       status_code: HTTP code. All below will miss if code is not 200.
--       name: name of person.
--       visible_id: visible ID of given person,
--       readable_id: Readable ID of given person
--       company: Working company
--
-- 2. GET http://www.ruuxee.com/api/web/v1/post_brief/<visible_id>
--   Purpose:
--       Get brief information of a post. shown as short text.
--   Return:
--       status_code: HTTP code. All below will miss if code is not 200.
--       status:
--           STATUS_REVIEWING = 1
--           STATUS_ACTIVATED = 2
--           STATUS_SUSPENDED = 3
--           STATUS_DELETED = 5
--       visible_id: visible ID of given post,
--       is_anonymous: Indicate if author is anonymous. 1 or 0.
--       author_name: Name of author. Not shown when is_anonymous == 1.
--       author_visible_id: Visible ID of author.
--       author_readable_id: Readable ID of author.
--       title: Title of post
--       brief_text: A short brief of post.
--
-- 3. GET http://www.ruuxee.com/api/web/v1/post/<post_visible_id>
--   Purpose:
--       Get brief information of a post. shown as full text.
--   Return:
--       status_code: HTTP code. All below will miss if code is not 200.
--       status:
--           STATUS_REVIEWING = 1
--           STATUS_ACTIVATED = 2
--           STATUS_SUSPENDED = 3
--           STATUS_DELETED = 5
--       is_anonymous: Indicate if author is anonymous. 1 or 0.
--       author_visible_id: Visible ID of author.
--       title: Title of post
--       brief_text: A short brief of post.
--       written_timestamp: Timestamp (in second) that the post is written.
--       content_html: Content in HTML.
--
-- 4. GET http://www.ruuxee.com/api/web/v1/follow/topic/<topic_visible_id>
--   Purpose
--       Make current person follow a topic.
--   Status
--       status_code: HTTP code. All below will miss if code is not 200.
--
-- 5. GET http://www.ruuxee.com/api/web/v1/unfollow/topic/<topic_visible_id>
--   Purpose
--       Make current person unfollow a topic.
--   Status
--       status_code: HTTP code. All below will miss if code is not 200.
--
-- 6. GET http://www.ruuxee.com/api/web/v1/follow/person/<person_visible_id>
--   Purpose
--       Make current person follow another person.
--   Status
--       status_code: HTTP code. All below will miss if code is not 200.
--
-- 7. GET http://www.ruuxee.com/api/web/v1/unfollow/person/<person_visible_id>
--   Purpose
--       Make current person unfollow another person.
--   Status
--       status_code: HTTP code. All below will miss if code is not 200.
--
-- 8. GET http://www.ruuxee.com/api/web/v1/upvote/post/<post_visible_id>
--   Purpose
--       Make current person upvote a post.
--   Status
--       status_code: HTTP code. All below will miss if code is not 200.
--
-- 9. GET http://www.ruuxee.com/api/web/v1/downvote/post/<post_visible_id>
--   Purpose
--       Make current person downvote a post.
--   Status
--       status_code: HTTP code. All below will miss if code is not 200.
--
-- 10. GET http://www.ruuxee.com/api/web/v1/neutralize/post/<post_visible_id>
--   Purpose
--       Make current person neutralize a post (neither upvote nor downvote).
--   Status
--       status_code: HTTP code. All below will miss if code is not 200.
--
-- 11. GET http://www.ruuxee.com/api/web/v1/timeline/range/<begin>/<end>
--   Purpose
--       Get timeline range started from latest.
--   Status
--       status_code: HTTP code. All below will miss if code is not 200.
--       data: A list of items below...
--       [
--          {
--            timestamp: When this action Happens.
--            action: ID of action
--            action_display: Display name of action.
--            "from"
--            {
--                same fields of get_person_brief
--            }
--            "to"
--            {
--                same fields of get_topic_brief, get_person_brief or
--                get_post_brief
--            }
--       ]
--
-- 12. GET http://www.ruuxee.com/api/web/v1/notification/range/<begin>/<end>
--   Purpose
--       Get notification range started from latest. A notification
--       is the action performed by other person but target current
--       logged on user.
--   Status
--       status_code: HTTP code. All below will miss if code is not 200.
--       data: A list of items below...
--       [
--          {
--            timestamp: When this action Happens.
--            action: ID of action
--            action_display: Display name of action.
--            "from"
--            {
--                same fields of get_person_brief
--            }
--            "to"
--            {
--                same fields of get_topic_brief, get_person_brief or
--                get_post_brief
--            }
--       ]
--
--
-- NOTE
-- a. All add* operations must use PUT to retrieve visible_ids.
-- b. The original person visible ID is ALWAYS invisible because they
--    are stored in cookie (web API) or header (oauth2 API)
