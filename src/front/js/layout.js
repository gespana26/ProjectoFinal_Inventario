import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import ScrollToTop from "./component/scrollToTop";
import { BackendURL } from "./component/backendURL";

import Login from './pages/Login.jsx';
import Signup from './pages/Signup.jsx';
import RegisterInformation from './pages/RegisterInformation.jsx';
import Products from './pages/Products.jsx';
import Clients from './pages/Clients.jsx';
import Sales from './pages/Sales.jsx';
import Reports from './pages/Reports.jsx';
import MainMenu from './pages/MainMenu.jsx';
import Profile from './pages/Profile.jsx';
import injectContext from "./store/appContext";
import UserApproval from './pages/UserApproval.jsx';
import PruebaSales_ from './pages/PruebaSales_.jsx';
import ProductsEntry from './pages/ProductsEntry.jsx';
import ProductsMenu from './pages/ProductsMenu.jsx'; 
import States from './pages/States.jsx';
import ReportAmountSold from './pages/ReportAmountSold.jsx';  
import ProductClientReport from './pages/ProductClientReport.jsx';

const Layout = () => {
    const basename = process.env.BASENAME || "";

    if (!process.env.BACKEND_URL || process.env.BACKEND_URL === "") return <BackendURL />;

    return (
        <div>
            <BrowserRouter basename={basename}>
                <ScrollToTop>
                    <Routes>
                        <Route element={<Login />} path="/" />
                        <Route element={<Login />} path="/login" />
                        <Route element={<Signup />} path="/signup" />
                        <Route element={<RegisterInformation />} path="/register-information" />
                        <Route element={<MainMenu />} path="/main-menu" />
                        <Route element={<ProductsMenu />} path="/products-menu" /> 
                        <Route element={<Products />} path="/products" />
                        <Route element={<ProductsEntry />} path="/products-entry" /> 
                        <Route element={<Clients />} path="/clients" />
                        <Route element={<Sales />} path="/sales" />
                        <Route element={<Reports />} path="/reports" />
                        <Route element={<Profile />} path="/profile" /> 
                        <Route element={<PruebaSales_ />} path="/PruebaSales" />
                        <Route element={<UserApproval />} path="/user-approval" />
                        <Route element={<States />} path="/states" />
                        <Route element={<ReportAmountSold />} path="/report-amount-sold" /> 
                        <Route element={<ProductClientReport />} path="/product-client-report" /> 
                        <Route element={<h1>Not found!</h1>} path="*" />
                    </Routes>
                </ScrollToTop>
            </BrowserRouter>
        </div>
    );
};

export default injectContext(Layout);
