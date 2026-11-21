import { Component, computed, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { HaService } from '../ha.service';

const ICONS: Record<string, string> = {
  'clear-night': '🌙', cloudy: '☁️', fog: '🌫️', hail: '🌨️', lightning: '⚡',
  'lightning-rainy': '⛈️', partlycloudy: '⛅', pouring: '🌧️', rainy: '🌦️',
  snowy: '❄️', 'snowy-rainy': '🌨️', sunny: '☀️', windy: '💨', 'windy-variant': '💨', exceptional: '❗',
};

@Component({
  selector: 'app-weather-card',
  imports: [DatePipe],
  template: `
    <section class="panel card">
      <h2 class="card-title">☁ Météo</h2>
      <div class="now">
        <div class="icon">{{ icon(w()?.state) }}</div>
        <div>
          <div class="temp">{{ round(w()?.attributes?.['temperature']) }}<small>°C</small></div>
          <div class="muted">Ressenti {{ w()?.attributes?.['apparent_temperature'] ?? '–' }}°</div>
        </div>
        <ul class="side">
          <li>Humidité <b>{{ w()?.attributes?.['humidity'] ?? '–' }} %</b></li>
          <li>Vent <b>{{ wind() }}</b></li>
          <li>Pression <b>{{ w()?.attributes?.['pressure'] ?? '–' }}</b></li>
        </ul>
      </div>
      <h3 class="sub">Prévisions horaires</h3>
      <div class="hours">
        @for (f of forecast(); track f.datetime) {
          <div class="h">
            <span class="muted">{{ f.datetime | date: 'HH:mm' }}</span>
            <span class="i">{{ icon(f.condition) }}</span>
            <b>{{ round(f.temperature) }}°</b>
            <span class="rain">{{ f.precipitation ?? 0 }} mm</span>
          </div>
        }
      </div>
      <div class="mini">
        <div class="panel"><span class="muted">Ext. chaudière</span><b>{{ ext() }} °C</b></div>
        <div class="panel"><span class="muted">Eau chaude</span><b>{{ ecs() }} °C</b></div>
      </div>
    </section>
  `,
  styles: `
    .card { padding: 16px; height: 100%; }
    .card-title { color: var(--text); }
    .now { display: flex; gap: 14px; align-items: center; }
    .icon { font-size: 54px; }
    .temp { font-size: 46px; font-weight: 300; line-height: 1; small { font-size: 18px; color: var(--muted); } }
    .muted { color: var(--muted); font-size: 12px; }
    .side { list-style: none; margin: 0 0 0 auto; padding: 0 0 0 14px; border-left: 1px solid var(--border); font-size: 12px; color: var(--muted); b { display: block; color: var(--text); font-size: 14px; margin-bottom: 4px; } }
    .sub { font-size: 12px; letter-spacing: 1.5px; text-transform: uppercase; color: var(--muted); margin: 18px 0 8px; }
    .hours { display: grid; grid-template-columns: repeat(auto-fit, minmax(54px, 1fr)); gap: 6px; text-align: center; }
    .h { display: flex; flex-direction: column; gap: 3px; padding: 8px 2px; border-radius: 10px; background: rgba(255,255,255,.03); .i { font-size: 22px; } .rain { font-size: 10px; color: var(--cyan); } }
    .mini { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 14px; .panel { padding: 10px 12px; display: flex; flex-direction: column; b { font-size: 20px; } } }
  `,
})
export class WeatherCard implements OnInit, OnDestroy {
  private ha = inject(HaService);
  readonly forecast = signal<any[]>([]);
  readonly w = computed(() => this.ha.get('weather.maison'));
  private unsub?: () => void;

  async ngOnInit() {
    this.unsub = await this.ha.subscribeHourlyForecast('weather.maison', (f) => this.forecast.set(f.slice(0, 7)));
  }
  ngOnDestroy() { this.unsub?.(); }

  icon(c?: string) { return ICONS[c ?? ''] ?? '🌡️'; }
  round(n: any) { return isNaN(Number(n)) ? '–' : Math.round(Number(n)); }
  wind() {
    const a = this.w()?.attributes;
    const v = Number(a?.['wind_speed']);
    return isNaN(v) ? '–' : `${v.toFixed(1)} ${a?.['wind_speed_unit'] ?? ''}`;
  }
  ext() { return this.fmt(this.ha.num('sensor.vicare_outside_temperature')); }
  ecs() { return this.fmt(this.ha.num('sensor.temperature_chauffe_eau')); }
  private fmt(n: number) { return isNaN(n) ? '–' : n.toFixed(1); }
}
