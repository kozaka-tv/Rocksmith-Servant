import {HttpClient, HttpClientModule} from '@angular/common/http';
import {Component, OnInit} from '@angular/core';


@Component({
    selector: 'app-playlists',
    imports: [
    HttpClientModule
],
    templateUrl: './playlists.component.html',
    styleUrl: './playlists.component.css'
})
export class PlaylistsComponent implements OnInit {
  playlists: any[] = [];

  constructor(private http: HttpClient) {
  }

  ngOnInit(): void {
    // Connect to Microservice 1 APIs
    this.http.get<any[]>('http://localhost:8000/example').subscribe((response) => {
      this.playlists = response;
    });
  }
}
