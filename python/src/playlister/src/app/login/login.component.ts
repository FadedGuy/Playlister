import { Component } from '@angular/core';
import { FormControl, NgModel } from '@angular/forms';
import { Validators } from '@angular/forms';

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

  constructor(private loginService: LoginService){}

  login(){
    if(this.username.valid && this.password.valid){
      console.log(this.username.value + " " + this.password.value);
      this.loginService
        .postLogin(this.username.value, this.password.value)
        .subscribe(res => console.log(res));
    } else{
      console.error("Invalid");
    }
  }
}
