import { Component, inject } from '@angular/core';
import { HaService } from '../ha.service';

@Component({
  selector: 'app-rooms-card',
  template: `
    <section class="panel card">
      <h2 class="card-title">⌂ Rooms</h2>
      <div class="rooms">
        @for (r of rooms; track r.id) {
          <div class="room">
            <span>{{ r.name }}</span>
            <b>🌡 {{ temp(r.id) }}</b>
            <small [class]="'c-' + status(r.id)">{{ label(r.id) }}</small>
          </div>
        }
      </div>
    </section>
  `,
  styles: `
    .card { padding: 16px; }
    .rooms { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
    .room { display: flex; flex-direction: column; gap: 4px; padding: 14px; border-radius: 14px; border: 1px solid var(--border); background: linear-gradient(135deg, rgba(8,22,38,.95), rgba(20,50,70,.7));
      span { font-size: 13px; } b { font-size: 22px; color: #ff9f5a; font-weight: 600; } small { font-size: 12px; }
      .c-ok { color: #4ade80; } .c-cold { color: var(--cyan); } .c-hot { color: var(--orange); } .c-na { color: var(--muted); } }
  `,
})
export class RoomsCard {
  private ha = inject(HaService);
  readonly rooms = [
    { id: 'sensor.honeywell_3', name: 'Salon' },
    { id: 'sensor.honeywell_4', name: 'Salle à manger' },
    { id: 'sensor.honeywell_5', name: 'Cuisine' },
    { id: 'sensor.honeywell_8', name: 'Chambre Emma' },
    { id: 'sensor.honeywell_9', name: 'Chambre Louis' },
    { id: 'sensor.honeywell_10', name: 'Bureau' },
  ];
  temp(id: string) { const n = this.ha.num(id); return isNaN(n) ? '–' : n.toFixed(1) + ' °C'; }
  status(id: string) { const n = this.ha.num(id); return isNaN(n) ? 'na' : n < 18 ? 'cold' : n > 24 ? 'hot' : 'ok'; }
  label(id: string) { return { na: 'Indisponible', cold: 'Frais', hot: 'Chaud', ok: 'Confortable' }[this.status(id)]; }
}
