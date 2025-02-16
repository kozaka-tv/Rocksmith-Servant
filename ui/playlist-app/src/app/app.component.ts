import { Component } from '@angular/core';
// import { RouterOutlet } from '@angular/router';
import {PlaylistsComponent} from "./playlists/playlists.component";

@Component({
  selector: 'app-root',
  standalone: true,
  // imports: [RouterOutlet, PlaylistsComponent],
  imports: [PlaylistsComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'playlist-app';
}
