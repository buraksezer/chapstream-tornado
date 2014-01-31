--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'SQL_ASCII';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: posts; Type: TABLE; Schema: public; Owner: csdbuser; Tablespace: 
--

CREATE TABLE posts (
    id bigint NOT NULL,
    body text,
    is_draft boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    user_id integer
);


ALTER TABLE public.posts OWNER TO csdbuser;

--
-- Name: seq_post_id; Type: SEQUENCE; Schema: public; Owner: csdbuser
--

CREATE SEQUENCE seq_post_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_post_id OWNER TO csdbuser;

--
-- Name: seq_user_id; Type: SEQUENCE; Schema: public; Owner: csdbuser
--

CREATE SEQUENCE seq_user_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_user_id OWNER TO csdbuser;

--
-- Name: seq_user_relation_id; Type: SEQUENCE; Schema: public; Owner: csdbuser
--

CREATE SEQUENCE seq_user_relation_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_user_relation_id OWNER TO csdbuser;

--
-- Name: user_relations; Type: TABLE; Schema: public; Owner: csdbuser; Tablespace: 
--

CREATE TABLE user_relations (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    chap_id integer NOT NULL,
    is_banned boolean
);


ALTER TABLE public.user_relations OWNER TO csdbuser;

--
-- Name: users; Type: TABLE; Schema: public; Owner: csdbuser; Tablespace: 
--

CREATE TABLE users (
    id bigint NOT NULL,
    name character varying NOT NULL,
    fullname character varying,
    email character varying NOT NULL,
    salt character varying NOT NULL,
    hash character varying NOT NULL,
    is_admin boolean,
    is_hidden boolean,
    bio text,
    sign_up_date timestamp without time zone,
    last_seen timestamp without time zone
);


ALTER TABLE public.users OWNER TO csdbuser;

--
-- Name: posts_pkey; Type: CONSTRAINT; Schema: public; Owner: csdbuser; Tablespace: 
--

ALTER TABLE ONLY posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- Name: user_relations_pkey; Type: CONSTRAINT; Schema: public; Owner: csdbuser; Tablespace: 
--

ALTER TABLE ONLY user_relations
    ADD CONSTRAINT user_relations_pkey PRIMARY KEY (id);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: csdbuser; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: posts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: csdbuser
--

ALTER TABLE ONLY posts
    ADD CONSTRAINT posts_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

