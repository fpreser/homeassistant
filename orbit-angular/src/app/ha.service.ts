import { Injectable, signal, computed } from '@angular/core';
import {
  Connection,
  HassEntities,
  HassEntity,
  createConnection,
  createLongLivedTokenAuth,
  subscribeEntities,
} from 'home-assistant-js-websocket';

const LS_URL = 'orbit.url';
const LS_TOKEN = 'orbit.token';

@Injectable({ providedIn: 'root' })
export class HaService {
  private conn?: Connection;
  readonly entities = signal<HassEntities>({});
  readonly status = signal<'login' | 'connecting' | 'ready' | 'error'>('login');
  readonly error = signal('');
  readonly url = signal(localStorage.getItem(LS_URL) ?? location.origin);
  readonly connected = computed(() => this.status() === 'ready');

  constructor() {
    if (localStorage.getItem(LS_TOKEN)) this.connect(this.url(), localStorage.getItem(LS_TOKEN)!);
  }

  async connect(url: string, token: string) {
    this.status.set('connecting');
    try {
      url = url.replace(/\/+$/, '');
      this.conn = await createConnection({ auth: createLongLivedTokenAuth(url, token) });
      localStorage.setItem(LS_URL, url);
      localStorage.setItem(LS_TOKEN, token);
      this.url.set(url);
      subscribeEntities(this.conn, (e) => this.entities.set(e));
      this.status.set('ready');
    } catch (e) {
      this.error.set(typeof e === 'number' ? 'Connexion refusée (token invalide ?)' : String(e));
      this.status.set('error');
    }
  }

  logout() {
    localStorage.removeItem(LS_TOKEN);
    this.conn?.close();
    this.status.set('login');
  }

  get(id: string): HassEntity | undefined {
    return this.entities()[id];
  }

  /** Etat numerique (NaN si indisponible). */
  num(id: string): number {
    return Number(this.entities()[id]?.state ?? NaN);
  }

  callService(domain: string, service: string, data: object) {
    return this.conn?.sendMessagePromise({ type: 'call_service', domain, service, service_data: data });
  }

  toggle(id: string) {
    return this.callService('homeassistant', 'toggle', { entity_id: id });
  }

  subscribeHourlyForecast(entityId: string, cb: (f: any[]) => void) {
    return this.conn!.subscribeMessage<{ forecast: any[] }>((m) => cb(m.forecast), {
      type: 'weather/subscribe_forecast',
      forecast_type: 'hourly',
      entity_id: entityId,
    });
  }

  async history(ids: string[], hours: number): Promise<Record<string, { s: string; lu: number }[]>> {
    const end = new Date();
    const start = new Date(end.getTime() - hours * 3600_000);
    return this.conn!.sendMessagePromise({
      type: 'history/history_during_period',
      start_time: start.toISOString(),
      end_time: end.toISOString(),
      entity_ids: ids,
      minimal_response: true,
      no_attributes: true,
      significant_changes_only: false,
    });
  }
}
