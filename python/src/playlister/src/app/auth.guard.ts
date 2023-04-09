import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { Observable, tap, throwError } from 'rxjs';
import { catchError, switchMap, of } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from 'src/environments/environment';


@Injectable({
  providedIn: 'root'
})
export class AuthGuard {
  constructor(private http: HttpClient, private router: Router){}

  retrieveCookieMeanwhile() {
    const cookie = document.cookie.split(';').some((item) => item.trim().startsWith(`${environment.ACCESS_TOKEN_ID}`));
    if (cookie) {
      const url = `${environment.GATEWAY_SVC_ADDRESS}/validate`;
      let cookieStr = '';
      document.cookie.split(';').forEach((e) => {
        if (e.startsWith(`${environment.ACCESS_TOKEN_ID}`)) {
          cookieStr = e.split('=')[1];
        }
      });
      return cookieStr;
    }
    return cookie;
  }

  canActivate(): any {
    const cookieStr = this.retrieveCookieMeanwhile();
    if (cookieStr) {
      const url = `${environment.GATEWAY_SVC_ADDRESS}/validate`;

      const headers = new HttpHeaders().set('Authorization', cookieStr);
      return this.http.post(url, '', { headers: headers, withCredentials: true, responseType: 'text' })
        .pipe(
          tap((response: any) => {
            return response.status == 200;
          }),
          catchError((error: Error) => {
            this.router.navigate([''])
            return throwError(() => new Error(error.message));
          })
        )
        .subscribe()
    
      } 

    return false;
  }
}
