import { Component, OnInit } from '@angular/core';
import { AuthGuard } from '../auth.guard';
import jwtDecode from 'jwt-decode';
import { CookieService } from 'ngx-cookie-service';
import { environment } from 'src/environments/environment';
import { Router } from '@angular/router';
import { Location } from '@angular/common';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
// Add so when it changes from one route to another updates username 

export class HeaderComponent implements OnInit {
  username: string ="";

  constructor(private auth: AuthGuard, 
              private cookie: CookieService, 
              private router: Router,
              private location: Location) {}

  ngOnInit(): void {
    this.location.onUrlChange((url, state) => {
      this.checkUsername()
    })
  }

  checkUsername(){
    let cookieStr = this.auth.retrieveCookieMeanwhile();
    if(cookieStr){
      try{
        // No need to verify jwt info
        const decoded = jwtDecode(cookieStr) as {username:string};
        this.username = decoded.username;
      }
      catch(err){
        console.error(err);
      }
    }
  }

  logout() {
    let cookieStr = this.auth.retrieveCookieMeanwhile();
    if(cookieStr){
      this.cookie.delete(environment.ACCESS_TOKEN_ID);
      if(!this.auth.retrieveCookieMeanwhile()){
        this.username = "";
        this.router.navigateByUrl('/')
      }
    }
  }
}
