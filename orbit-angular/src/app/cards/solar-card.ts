import { Component, computed, inject } from '@angular/core';
import { HaService } from '../ha.service';

@Component({
  selector: 'app-solar-card',
  template: `
    <section class="panel card">
      <h2 class="card-title">☀ Solar <b>Live</b></h2>
      <div class="flow">
        <div class="orb amber top"><span class="ic">☀</span><small>SOLAR</small><b>{{ kw(solar()) }} kW</b></div>
        <div class="orb cyan left"><span class="ic">⌂</span><small>HOME</small><b>{{ kw(home()) }} kW</b></div>
        <div class="orb orange right">
          <span class="ic">⚡</span><small>{{ grid() < 0 ? 'TO GRID' : 'FROM GRID' }}</small><b>{{ kw(abs(grid())) }} kW</b>
        </div>
      </div>
      <div class="stats">
        <div><small>Produit aujourd'hui</small><b>{{ today() }} kWh</b></div>
        <div><small>Tesla</small><b>{{ kw(tesla()) }} kW</b></div>
        <div><small>Autoconsommation</small><b>{{ selfUse() }}</b></div>
      </div>
    </section>
  `,
  styles: `
    .card { padding: 16px; height: 100%; }
    .card-title { color: var(--amber); b { color: var(--text); } }
    .flow { position: relative; display: grid; grid-template-columns: 1fr 1fr 1fr; grid-template-rows: auto auto; gap: 10px; padding: 8px 0 16px;
      &::before { content: ''; position: absolute; inset: 20% 18% 6%; border: 1px solid rgba(56,214,255,.25); border-radius: 50%; pointer-events: none; } }
    .orb { aspect-ratio: 1; max-width: 150px; width: 100%; justify-self: center; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px;
      border: 2px solid var(--c); background: radial-gradient(circle, color-mix(in srgb, var(--c) 20%, transparent), rgba(8,22,38,.9)); box-shadow: 0 0 26px color-mix(in srgb, var(--c) 45%, transparent);
      .ic { font-size: 28px; color: var(--c); } small { letter-spacing: 2px; font-size: 11px; } b { color: var(--c); font-size: 20px; } }
    .amber { --c: var(--amber); } .cyan { --c: var(--cyan); } .orange { --c: var(--orange); }
    .top { grid-column: 2; grid-row: 1; } .left { grid-column: 1; grid-row: 2; } .right { grid-column: 3; grid-row: 2; }
    .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; div { padding: 10px; border-radius: 10px; background: rgba(255,255,255,.04); } small { display: block; color: var(--muted); font-size: 11px; } b { font-size: 18px; } }
  `,
})
export class SolarCard {
  private ha = inject(HaService);
  readonly solar = computed(() => this.ha.num('sensor.solar_total'));
  readonly home = computed(() => this.ha.num('sensor.power_home'));
  readonly grid = computed(() => this.ha.num('sensor.p1_meter_3c39e7284d28_active_power'));
  readonly tesla = computed(() => this.ha.num('sensor.power_tesla'));
  readonly today = computed(() => {
    const t = (this.ha.num('sensor.sb5_0_1av_41_208_daily_yield') || 0) + (this.ha.num('sensor.sb5_0_1av_41_345_daily_yield') || 0);
    return (t / 1000).toFixed(2);
  });
  readonly selfUse = computed(() => {
    const s = this.solar(), g = this.grid();
    if (!(s > 0)) return '–';
    const exported = Math.max(-(isNaN(g) ? 0 : g), 0);
    return Math.round(((s - Math.min(exported, s)) / s) * 100) + ' %';
  });
  abs(n: number) { return Math.abs(n); }
  kw(w: number) { return isNaN(w) ? '–' : (w / 1000).toFixed(2); }
}
