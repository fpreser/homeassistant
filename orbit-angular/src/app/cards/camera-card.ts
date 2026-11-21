import { Component, computed, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { HaService } from '../ha.service';

@Component({
  selector: 'app-camera-card',
  template: `
    <section class="panel card">
      <h2 class="card-title">▣ Caméras</h2>
      <div class="cam">
        @if (src(); as s) { <img [src]="s" alt="Sonnette" /> } @else { <span>Pas d'image</span> }
        <em>Sonnette</em>
      </div>
    </section>
  `,
  styles: `
    .card { padding: 16px; height: 100%; }
    .cam { position: relative; aspect-ratio: 16 / 10; border-radius: 10px; overflow: hidden; background: #000; display: grid; place-items: center; color: var(--muted);
      img { width: 100%; height: 100%; object-fit: cover; } em { position: absolute; left: 8px; top: 6px; font-style: normal; font-size: 11px; background: rgba(0,0,0,.55); padding: 2px 8px; border-radius: 6px; } }
  `,
})
export class CameraCard implements OnInit, OnDestroy {
  private ha = inject(HaService);
  private tick = signal(0);
  private timer?: number;
  readonly src = computed(() => {
    const pic = this.ha.get('camera.sonnette')?.attributes?.['entity_picture'];
    return pic ? `${this.ha.url()}${pic}${pic.includes('?') ? '&' : '?'}t=${this.tick()}` : '';
  });
  ngOnInit() { this.timer = window.setInterval(() => this.tick.update((n) => n + 1), 10_000); }
  ngOnDestroy() { clearInterval(this.timer); }
}
