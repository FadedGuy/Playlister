import { NgModule, inject } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { IndexComponent } from './index/index.component';
import { ApplicationComponent } from './application/application.component';
import { AuthGuard } from './auth.guard';

const routes: Routes = [
  {path: '', component: IndexComponent},
  {path: 'app', component: ApplicationComponent, canActivate: [() => inject(AuthGuard).canActivate()]}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
