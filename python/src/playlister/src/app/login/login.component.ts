import { Component } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Validators } from '@angular/forms';
import { Router } from '@angular/router';

import { LoginService } from './login.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
  providers: [LoginService],
})

export class LoginComponent {
  username = new FormControl('', [
    Validators.required,
    Validators.minLength(4),
    Validators.pattern('[a-zA-Z0-9]+'),
  ]);

  password = new FormControl('', [
    Validators.required,
  ]);

  messageLogin: string = "";
  constructor(private loginService: LoginService, private router: Router){}

  login(){
    if(this.username.valid && this.password.valid){
      this.loginService
        .login(this.username.value, this.password.value)
        .subscribe({
          next: () => {
            this.messageLogin = "Logged In!";
          },
          error: (e) => {
            console.error(e);
            this.messageLogin = e;
          },
          complete: () => {
            console.info("complete");
            this.router.navigate(['app']);
          }
        })
          
    } 
    else {
      console.error("Invalid");
    }
  }
}
