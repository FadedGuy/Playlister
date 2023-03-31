import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';

import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from 'src/environments/environment';
import { CookieService } from 'ngx-cookie-service';

@Injectable({
  providedIn: 'root'
})

export class LoginService {
    // private gatewayURL = environment.GATEWAY_SVC_ADDRESS;
    private gatewayURL = "http://api.playlister.com";
    constructor(private http: HttpClient, private cookie: CookieService){} 
  
    login(user: string|null, pass: string|null): Observable<any> {
        const url = `${this.gatewayURL}/login`;
        const encoded = btoa(user+":"+pass);
        const token = `Basic ${encoded}`;

        const headers = new HttpHeaders().set('Authorization', token);

        return this.http.post(url, "", {headers: headers, observe: 'response', withCredentials: true}).pipe(
          tap((response: any) => {
            // No es lo mejor pero como decia, esto de la api no funciona en localhost
            this.cookie.set(environment.ACCESS_TOKEN_ID, response.body[environment.ACCESS_TOKEN_ID]);
          }),
          catchError((error: any) => {
            return throwError(() => new Error(error.error));
          })
        );
    }
}
