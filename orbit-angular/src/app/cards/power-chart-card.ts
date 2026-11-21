import { Component, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { HaService } from '../ha.service';

interface Serie { id: string; label: string; color: string; path: string }

const W = 600, H = 200, BUCKETS = 96, HOURS = 24;
const SERIES = [
  { id: 'sensor.solar_total', label: 'Solar', color: '#ffc531' },
  { id: 'sensor.power_home', label: 'Home', color: '#ffffff' },
  { id: 'sensor.p1_meter_3c39e7284d28_active_power', label: 'Grid', color: '#38d6ff' },
];

@Component({
  selector: 'app-power-chart-card',
  template: `
    <section class="panel card">
      <h2 class="card-title">Power · 24 hours</h2>
      <div class="legend">
        @for (s of series(); track s.id) { <span><i [style.background]="s.color"></i>{{ s.label }}</span> }
      </div>
      <svg [attr.viewBox]="'0 0 ' + w + ' ' + h" preserveAspectRatio="none">
        @for (g of grid; track g) { <line x1="0" x2="600" [attr.y1]="g" [attr.y2]="g" /> }
        @for (s of series(); track s.id) { <path [attr.d]="s.path" [attr.stroke]="s.color" fill="none" stroke-width="2" vector-effect="non-scaling-stroke" /> }
      </svg>
      <div class="axis"><span>-24h</span><span>-12h</span><span>maintenant</span></div>
    </section>
  `,
  styles: `
    .card { padding: 16px; height: 100%; }
    .legend { display: flex; gap: 14px; font-size: 12px; color: var(--muted); i { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 5px; } }
    svg { width: 100%; height: 180px; margin-top: 8px; line { stroke: rgba(255,255,255,.08); } }
    .axis { display: flex; justify-content: space-between; font-size: 11px; color: var(--muted); }
  `,
})
export class PowerChartCard implements OnInit, OnDestroy {
  private ha = inject(HaService);
  readonly series = signal<Serie[]>([]);
  readonly w = W; readonly h = H;
  readonly grid = [0, 50, 100, 150, 200];
  private timer?: number;

  ngOnInit() {
    this.load();
    this.timer = window.setInterval(() => this.load(), 5 * 60_000);
  }
  ngOnDestroy() { clearInterval(this.timer); }

  private async load() {
    const data = await this.ha.history(SERIES.map((s) => s.id), HOURS);
    const t1 = Date.now() / 1000, t0 = t1 - HOURS * 3600;
    const sampled = SERIES.map((s) => {
      const pts = (data[s.id] ?? []).map((p) => ({ t: p.lu, v: Number(p.s) })).filter((p) => !isNaN(p.v));
      const out: number[] = [];
      let i = 0, last = pts[0]?.v ?? 0;
      for (let b = 0; b < BUCKETS; b++) {
        const t = t0 + ((b + 1) / BUCKETS) * (t1 - t0);
        while (i < pts.length && pts[i].t <= t) last = pts[i++].v;
        out.push(last);
      }
      return out;
    });
    const all = sampled.flat();
    const max = Math.max(1000, ...all), min = Math.min(0, ...all);
    const y = (v: number) => H - 6 - ((v - min) / (max - min)) * (H - 12);
    this.series.set(SERIES.map((s, k) => ({
      ...s,
      path: sampled[k].map((v, b) => `${b ? 'L' : 'M'}${((b / (BUCKETS - 1)) * W).toFixed(1)},${y(v).toFixed(1)}`).join(' '),
    })));
  }
}
