import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { SUPABASE_ANON, SUPABASE_CONFIGURED, SUPABASE_URL } from "./constants";

let client: SupabaseClient | null = null;

export function getSupabase(): SupabaseClient | null {
  if (!SUPABASE_CONFIGURED) return null;
  if (!client) {
    client = createClient(SUPABASE_URL, SUPABASE_ANON, {
      realtime: { params: { eventsPerSecond: 10 } },
    });
  }
  return client;
}
