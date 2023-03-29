import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';

import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class LoginService {
    gatewayURL = environment.GATEWAY_SVC_ADDRESS;
    // gatewayURL = "https://ytconverter.com/";
    constructor(private http: HttpClient){} 

    postLogin(user: string|null, pass: string|null): Observable<unknown> {
        const url = `${this.gatewayURL}/login`;
        const encoded = btoa(user+":"+pass);
        const token = `Basic ${encoded}`;

        const headers = new HttpHeaders().set('Authorization', token);

        return this.http.post(url, "", {headers: headers});
    }
}
