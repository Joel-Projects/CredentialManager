create or replace function credential_store.gen_state() returns trigger
	language plpgsql
as $$
BEGIN
	IF tg_op = 'INSERT' OR tg_op = 'UPDATE' THEN
		NEW.state = encode(public.digest(NEW.client_id, 'sha256'), 'hex');
		RETURN NEW;
	END IF;
END;
$$;

alter function gen_state() owner to postgres;
create trigger refresh_token_state_hashing_trigger
	before insert or update
	of client_id
	on credential_store.reddit_apps
	for each row
	execute procedure credential_store.gen_state();
