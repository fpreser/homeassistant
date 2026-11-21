import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HaService } from './ha.service';
import { WeatherCard } from './cards/weather-card';
import { SolarCard } from './cards/solar-card';
import { PowerChartCard } from './cards/power-chart-card';
import { CameraCard } from './cards/camera-card';
import { ControlsCard } from './cards/controls-card';
import { RoomsCard } from './cards/rooms-card';

@Component({
  selector: 'app-root',
  imports: [DatePipe, FormsModule, WeatherCard, SolarCard, PowerChartCard, CameraCard, ControlsCard, RoomsCard],
  styleUrl: './app.scss',
  templateUrl: './app.html',
})
export class App implements OnInit, OnDestroy {
  readonly ha = inject(HaService);
  readonly now = signal(new Date());
  url = this.ha.url();
  token = '';
  private timer?: number;

  ngOnInit() {
    this.timer = window.setInterval(() => this.now.set(new Date()), 1000);
  }
  ngOnDestroy() {
    clearInterval(this.timer);
  }
  login() {
    this.ha.connect(this.url, this.token.trim());
  }
}
