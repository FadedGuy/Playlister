import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private http: HttpClient, private router: Router){}

  canActivate(): boolean{
    // When set-cookie works, there is no need to send this as is, it would be sent automatically
    const cookie = document.cookie.split(';').some((item) => item.trim().startsWith(`${environment.ACCESS_TOKEN_ID}`));
    if(cookie){      
        console.log(cookie);
        return true;
        // const url = `${environment.GATEWAY_SVC_ADDRESS}/verify`;
        // this.http.post(url, "").pipe(
        //   tap((response: any) => {
        //     // route?
        //     return true;
        //   }),
        // );
      } 

      this.router.navigate(['']); // Navigate to the login page if the cookie is not available
      return false;
  }
}
