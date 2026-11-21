import { Component, inject } from '@angular/core';
import { HaService } from '../ha.service';

@Component({
  selector: 'app-controls-card',
  template: `
    <section class="panel card">
      <h2 class="card-title">Controls</h2>
      <div class="row">
        @for (c of controls; track c.id) {
          <button [class.on]="ha.get(c.id)?.state === 'on'" (click)="ha.toggle(c.id)">
            <span class="ic">{{ c.icon }}</span>
            <b>{{ c.name }}</b>
            <small>{{ ha.get(c.id)?.state === 'on' ? 'ON' : 'OFF' }}</small>
          </button>
        }
      </div>
    </section>
  `,
  styles: `
    .card { padding: 16px; height: 100%; }
    .row { display: grid; grid-template-columns: repeat(auto-fit, minmax(90px, 1fr)); gap: 10px; }
    button { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 14px 6px; border-radius: 14px; border: 1px solid var(--border); background: rgba(8,22,38,.78); color: var(--text); font: inherit; cursor: pointer;
      .ic { font-size: 26px; filter: grayscale(1); } small { font-size: 10px; letter-spacing: 1px; color: var(--muted); }
      &.on { border-color: var(--cyan); box-shadow: 0 0 14px rgba(56,214,255,.4); .ic { filter: none; } small { color: var(--cyan); } } }
  `,
})
export class ControlsCard {
  readonly ha = inject(HaService);
  readonly controls = [
    { id: 'light.terasse', name: 'Terrasse', icon: '💡' },
    { id: 'light.salon_exterieur', name: 'Salon ext.', icon: '💡' },
    { id: 'light.terasse_bois', name: 'Bois', icon: '💡' },
  ];
}
