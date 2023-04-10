import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';

import { Observable, throwError, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from 'src/environments/environment';
import { CookieService } from 'ngx-cookie-service';
import { AuthGuard } from '../auth.guard';

@Injectable({
  providedIn: 'root'
})

export class ApplicationService {
    private gatewayURL = environment.GATEWAY_SVC_ADDRESS;
    constructor(private http: HttpClient, private cookie: CookieService, private auth: AuthGuard){} 
  
    sendURL(urlStr: string): Observable<any> {
        const url = `${this.gatewayURL}/sendURL`;
        const cookieStr = this.auth.retrieveCookieMeanwhile();

        if (cookieStr) {
          const headers = new HttpHeaders().set('Authorization', cookieStr);
          return this.http.post(url, urlStr, { headers: headers, withCredentials: true, responseType: 'text' })
            .pipe(
              tap((response: any) => {
                console.log(response);
              }),
              catchError((error: Error) => {
                return throwError(() => new Error(error.message));
              })
            )
        } 
    
        return of(false);
    }

    retrieveURL(): Observable<any> {
        const url = `${this.gatewayURL}/download`;
        const cookieStr = this.auth.retrieveCookieMeanwhile();

        if (cookieStr) {
          const headers = new HttpHeaders().set('Authorization', cookieStr);
          return this.http.get(url, { headers: headers, withCredentials: true, responseType: 'text' })
            .pipe(
              tap((response: any) => {
                // console.log(response);
                return response;
              }),
              catchError((error: Error) => {
                return throwError(() => new Error(error.message));
              })
            )
        } 
    
        return of(false);
    }
}
