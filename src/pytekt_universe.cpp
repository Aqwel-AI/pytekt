/*
 * PyTekt — fast astronomy calculations (universe module)
 *
 * Optional native module: pytekt._pytekt_universe
 * Requires pybind11 and C++14 at build time.
 *
 * License: Apache-2.0
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>
#include <algorithm>
#include <limits>
#include <stdexcept>
#include <tuple>
#include <vector>

namespace py = pybind11;

static constexpr double PI = 3.14159265358979323846;
static constexpr double DEG2RAD = PI / 180.0;
static constexpr double RAD2DEG = 180.0 / PI;
static constexpr double J2000 = 2451545.0;
static constexpr double C_KM_S = 299792.458;  // km/s
static constexpr double C_M_S = 299792458.0;
static constexpr double OBLIQUITY_DEG = 23.4392911;
static constexpr double INF = std::numeric_limits<double>::infinity();

static inline double clampd(double v, double lo, double hi) {
    return std::max(lo, std::min(hi, v));
}

static inline double deg_to_rad(double d) { return d * DEG2RAD; }
static inline double rad_to_deg(double r) { return r * RAD2DEG; }

double gmst_hours(double jd) {
    double t = (jd - J2000) / 36525.0;
    double theta = 280.46061837
        + 360.98564736629 * (jd - J2000)
        + 0.000387933 * t * t
        - t * t * t / 38710000.0;
    double h = std::fmod(theta, 360.0);
    if (h < 0) h += 360.0;
    return h / 15.0;
}

std::pair<double, double> equatorial_to_horizontal(
    double ra_hours, double dec_deg,
    double latitude_deg, double longitude_deg, double jd)
{
    double ha = (gmst_hours(jd) + longitude_deg / 15.0 - ra_hours) * 15.0;
    double ha_rad = deg_to_rad(ha);
    double dec_rad = deg_to_rad(dec_deg);
    double lat_rad = deg_to_rad(latitude_deg);

    double sin_alt = std::sin(dec_rad) * std::sin(lat_rad)
        + std::cos(dec_rad) * std::cos(lat_rad) * std::cos(ha_rad);
    double alt = std::asin(clampd(sin_alt, -1.0, 1.0));

    double cos_alt = std::cos(alt);
    double cos_az = (std::sin(dec_rad) - std::sin(alt) * std::sin(lat_rad))
        / (cos_alt * std::cos(lat_rad) + 1e-15);
    cos_az = clampd(cos_az, -1.0, 1.0);
    double sin_az = -std::cos(dec_rad) * std::sin(ha_rad) / (cos_alt + 1e-15);
    double az = std::atan2(sin_az, cos_az);
    if (az < 0) az += 2.0 * PI;

    return {rad_to_deg(alt), rad_to_deg(az)};
}

py::tuple equatorial_to_horizontal_batch(
    py::array_t<double> ra_hours,
    py::array_t<double> dec_deg,
    double latitude_deg, double longitude_deg, double jd)
{
    py::buffer_info bra = ra_hours.request(), bdec = dec_deg.request();
    if (bra.ndim != 1 || bdec.ndim != 1 || bra.shape[0] != bdec.shape[0]) {
        throw std::runtime_error("equatorial_to_horizontal_batch: 1D arrays of equal length required");
    }
    size_t n = bra.shape[0];
    const double* pra = static_cast<const double*>(bra.ptr);
    const double* pdec = static_cast<const double*>(bdec.ptr);

    auto alt = py::array_t<double>(n);
    auto az = py::array_t<double>(n);
    double* palt = static_cast<double*>(alt.request().ptr);
    double* paz = static_cast<double*>(az.request().ptr);

    for (size_t i = 0; i < n; ++i) {
        auto hor = equatorial_to_horizontal(pra[i], pdec[i], latitude_deg, longitude_deg, jd);
        palt[i] = hor.first;
        paz[i] = hor.second;
    }
    return py::make_tuple(alt, az);
}

double angular_separation_deg(
    double ra1_hours, double dec1_deg,
    double ra2_hours, double dec2_deg)
{
    double a1 = deg_to_rad(ra1_hours * 15.0);
    double d1 = deg_to_rad(dec1_deg);
    double a2 = deg_to_rad(ra2_hours * 15.0);
    double d2 = deg_to_rad(dec2_deg);
    double cos_sep = std::sin(d1) * std::sin(d2)
        + std::cos(d1) * std::cos(d2) * std::cos(a1 - a2);
    return rad_to_deg(std::acos(clampd(cos_sep, -1.0, 1.0)));
}

std::pair<double, double> equatorial_to_galactic(double ra_hours, double dec_deg) {
    double ra = deg_to_rad(ra_hours * 15.0);
    double dec = deg_to_rad(dec_deg);
    double ra_gp = deg_to_rad(192.85948);
    double dec_gp = deg_to_rad(27.12825);
    double l_cp = deg_to_rad(122.93192);

    double sin_b = std::sin(dec_gp) * std::sin(dec)
        + std::cos(dec_gp) * std::cos(dec) * std::cos(ra - ra_gp);
    double b = std::asin(clampd(sin_b, -1.0, 1.0));
    double y = std::cos(dec) * std::sin(ra - ra_gp);
    double x = std::sin(dec_gp) * std::cos(dec) * std::cos(ra - ra_gp)
        - std::cos(dec_gp) * std::sin(dec);
    double l = std::atan2(y, x) + l_cp;
    if (l < 0) l += 2.0 * PI;
    return {rad_to_deg(l), rad_to_deg(b)};
}

double moon_phase_fraction(double jd) {
    double t = (jd - J2000) / 36525.0;
    double d = std::fmod(297.8501921 + 445267.1114034 * t, 360.0);
    if (d < 0) d += 360.0;
    return (1.0 - std::cos(deg_to_rad(d))) / 2.0;
}

double e_z(double z, double Om0, double Ode0) {
    return std::sqrt(Om0 * std::pow(1.0 + z, 3) + Ode0);
}

double comoving_distance_mpc(double z, double H0, double Om0, double Ode0, int steps) {
    if (z <= 0) return 0.0;
    if (steps < 1) steps = 1;
    double dz = z / steps;
    double total = 0.0;
    for (int i = 0; i < steps; ++i) {
        double zi = (i + 0.5) * dz;
        total += dz / e_z(zi, Om0, Ode0);
    }
    return (C_KM_S / H0) * total;
}

double luminosity_distance_mpc(double z, double H0, double Om0, double Ode0, int steps) {
    return comoving_distance_mpc(z, H0, Om0, Ode0, steps) * (1.0 + z);
}

double lookback_time_gyr(double z, double H0, double Om0, double Ode0, int steps) {
    if (z <= 0) return 0.0;
    if (steps < 1) steps = 1;
    double h = H0 / 100.0;
    double dz = z / steps;
    double total = 0.0;
    for (int i = 0; i < steps; ++i) {
        double zi = (i + 0.5) * dz;
        total += dz / ((1.0 + zi) * e_z(zi, Om0, Ode0));
    }
    return 9.77813 / h * total;
}

double flux_to_magnitude(double flux, double flux_zero) {
    if (flux <= 0) throw std::runtime_error("flux must be positive");
    return -2.5 * std::log10(flux / flux_zero);
}

double magnitude_to_flux(double mag, double flux_zero) {
    return flux_zero * std::pow(10.0, -0.4 * mag);
}

double distance_modulus(double distance_pc) {
    if (distance_pc <= 0) throw std::runtime_error("distance_pc must be positive");
    return 5.0 * std::log10(distance_pc / 10.0);
}

std::pair<double, double> horizontal_to_equatorial(
    double alt_deg, double az_deg,
    double latitude_deg, double longitude_deg, double jd)
{
    double alt = deg_to_rad(alt_deg);
    double az = deg_to_rad(az_deg);
    double lat = deg_to_rad(latitude_deg);
    double sin_dec = std::sin(alt) * std::sin(lat)
        + std::cos(alt) * std::cos(lat) * std::cos(az);
    double dec = std::asin(clampd(sin_dec, -1.0, 1.0));
    double cos_ha = (std::sin(alt) - std::sin(dec) * std::sin(lat))
        / (std::cos(dec) * std::cos(lat) + 1e-15);
    cos_ha = clampd(cos_ha, -1.0, 1.0);
    double sin_ha = -std::cos(alt) * std::sin(az) / (std::cos(dec) + 1e-15);
    double ha = std::atan2(sin_ha, cos_ha);
    double ha_deg = rad_to_deg(ha);
    double ra_deg = std::fmod(gmst_hours(jd) * 15.0 + longitude_deg - ha_deg, 360.0);
    if (ra_deg < 0) ra_deg += 360.0;
    return {ra_deg / 15.0, rad_to_deg(dec)};
}

double lst_hours(double jd, double longitude_deg) {
    double lst = gmst_hours(jd) + longitude_deg / 15.0;
    lst = std::fmod(lst, 24.0);
    if (lst < 0) lst += 24.0;
    return lst;
}

std::pair<double, double> ecliptic_to_equatorial(double lon_deg, double lat_deg) {
    double lon = deg_to_rad(lon_deg);
    double lat = deg_to_rad(lat_deg);
    double eps = deg_to_rad(OBLIQUITY_DEG);
    double sin_dec = std::sin(lat) * std::cos(eps)
        + std::cos(lat) * std::sin(eps) * std::sin(lon);
    double dec = std::asin(clampd(sin_dec, -1.0, 1.0));
    double y = std::sin(lon) * std::cos(eps) - std::tan(lat) * std::sin(eps);
    double x = std::cos(lon);
    double ra = std::atan2(y, x);
    if (ra < 0) ra += 2.0 * PI;
    return {rad_to_deg(ra) / 15.0, rad_to_deg(dec)};
}

py::tuple ecliptic_to_equatorial_batch(py::array_t<double> lon_deg, py::array_t<double> lat_deg) {
    py::buffer_info blon = lon_deg.request(), blat = lat_deg.request();
    if (blon.ndim != 1 || blat.ndim != 1 || blon.shape[0] != blat.shape[0]) {
        throw std::runtime_error("ecliptic_to_equatorial_batch: 1D arrays of equal length required");
    }
    size_t n = blon.shape[0];
    const double* plon = static_cast<const double*>(blon.ptr);
    const double* plat = static_cast<const double*>(blat.ptr);
    auto ra = py::array_t<double>(n);
    auto dec = py::array_t<double>(n);
    double* pra = static_cast<double*>(ra.request().ptr);
    double* pdec = static_cast<double*>(dec.request().ptr);
    for (size_t i = 0; i < n; ++i) {
        auto eq = ecliptic_to_equatorial(plon[i], plat[i]);
        pra[i] = eq.first;
        pdec[i] = eq.second;
    }
    return py::make_tuple(ra, dec);
}

std::pair<double, double> precess(
    double ra_hours, double dec_deg,
    double from_epoch, double to_epoch)
{
    if (std::abs(from_epoch - to_epoch) < 1e-9) {
        return {ra_hours, dec_deg};
    }
    double t0 = (from_epoch - 2000.0) / 100.0;
    double t = (to_epoch - 2000.0) / 100.0;
    double zeta_a = (2306.2181 + 1.39656 * t0 - 0.000139 * t0 * t0) * (t - t0) / 3600.0;
    double z_a = (2306.2181 + 1.39656 * t0) * (t - t0) / 3600.0
        + (0.30188 - 0.000344 * t0) * (t - t0) * (t - t0) / 3600.0;
    double theta_a = (2004.3109 - 0.85330 * t0) * (t - t0) / 3600.0
        - (0.42665 + 0.000217 * t0) * (t - t0) * (t - t0) / 3600.0;
    double ra = ra_hours * 15.0;
    double dec_new = dec_deg + theta_a * std::cos(deg_to_rad(ra));
    double ra_new = ra + z_a + zeta_a / std::cos(deg_to_rad(dec_deg + 1e-6));
    return {ra_new / 15.0, dec_new};
}

double air_mass(double altitude_deg, bool pickering) {
    if (altitude_deg <= 0) return INF;
    if (pickering) {
        return 1.0 / (std::sin(deg_to_rad(altitude_deg))
            + 0.50572 * std::pow(altitude_deg + 6.07995, -1.6364));
    }
    return 1.0 / std::sin(deg_to_rad(altitude_deg));
}

py::array_t<double> air_mass_batch(py::array_t<double> altitude_deg, bool pickering) {
    py::buffer_info b = altitude_deg.request();
    if (b.ndim != 1) throw std::runtime_error("air_mass_batch: 1D array required");
    size_t n = b.shape[0];
    const double* pin = static_cast<const double*>(b.ptr);
    auto out = py::array_t<double>(n);
    double* pout = static_cast<double*>(out.request().ptr);
    for (size_t i = 0; i < n; ++i) {
        pout[i] = air_mass(pin[i], pickering);
    }
    return out;
}

bool is_circumpolar(double dec_deg, double latitude_deg) {
    return dec_deg > (90.0 - std::abs(latitude_deg));
}

py::dict rise_set_approx(
    double ra_hours, double dec_deg,
    double latitude_deg, double longitude_deg, double jd)
{
    py::dict result;
    double lat = deg_to_rad(latitude_deg);
    double dec = deg_to_rad(dec_deg);
    double cos_h0 = -std::tan(lat) * std::tan(dec);
    if (cos_h0 > 1.0) {
        result["rise"] = py::none();
        result["transit"] = py::none();
        result["set"] = py::none();
        result["circumpolar"] = false;
        result["never_rises"] = true;
        return result;
    }
    if (cos_h0 < -1.0) {
        result["rise"] = py::none();
        result["transit"] = py::none();
        result["set"] = py::none();
        result["circumpolar"] = true;
        result["never_rises"] = false;
        return result;
    }
    double h0 = std::acos(cos_h0);
    double h0_hours = rad_to_deg(h0) / 15.0;
    double gmst0 = gmst_hours(jd);
    double transit_offset = std::fmod(ra_hours - gmst0 - longitude_deg / 15.0, 24.0);
    if (transit_offset < 0) transit_offset += 24.0;
    double rise_offset = std::fmod(transit_offset - h0_hours, 24.0);
    if (rise_offset < 0) rise_offset += 24.0;
    double set_offset = std::fmod(transit_offset + h0_hours, 24.0);
    if (set_offset < 0) set_offset += 24.0;
    double jd0 = jd - std::fmod(jd, 1.0);
    result["rise"] = jd0 + rise_offset / 24.0;
    result["transit"] = jd0 + transit_offset / 24.0;
    result["set"] = jd0 + set_offset / 24.0;
    result["circumpolar"] = false;
    result["never_rises"] = false;
    result["hour_angle_at_rise"] = h0_hours;
    return result;
}

double moon_illumination(double jd) {
    double phase = moon_phase_fraction(jd);
    return std::abs(std::cos(PI * phase));
}

double true_anomaly_from_mean(double M_deg, double e, double tol) {
    double M = deg_to_rad(std::fmod(M_deg, 360.0));
    double E = (e < 0.8) ? M : PI;
    for (int i = 0; i < 50; ++i) {
        double dE = (E - e * std::sin(E) - M) / (1.0 - e * std::cos(E));
        E -= dE;
        if (std::abs(dE) < tol) break;
    }
    double nu = 2.0 * std::atan2(
        std::sqrt(1.0 + e) * std::sin(E / 2.0),
        std::sqrt(1.0 - e) * std::cos(E / 2.0));
    double nu_deg = rad_to_deg(nu);
    nu_deg = std::fmod(nu_deg, 360.0);
    if (nu_deg < 0) nu_deg += 360.0;
    return nu_deg;
}

double mean_anomaly_from_true(double nu_deg, double e) {
    double nu = deg_to_rad(nu_deg);
    double ea = 2.0 * std::atan2(
        std::sqrt(1.0 - e) * std::sin(nu / 2.0),
        std::sqrt(1.0 + e) * std::cos(nu / 2.0));
    return rad_to_deg(ea - e * std::sin(ea));
}

double kepler_third_law(double a, double mu) {
    return 2.0 * PI * std::sqrt(a * a * a / mu);
}

py::dict hohmann_transfer(double r1, double r2, double mu) {
    if (r2 < r1) std::swap(r1, r2);
    double v1 = std::sqrt(mu / r1);
    double v2 = std::sqrt(mu / r2);
    double a_transfer = (r1 + r2) / 2.0;
    double v_peri = std::sqrt(mu * (2.0 / r1 - 1.0 / a_transfer));
    double v_apo = std::sqrt(mu * (2.0 / r2 - 1.0 / a_transfer));
    double dv1 = v_peri - v1;
    double dv2 = v2 - v_apo;
    py::dict result;
    result["dv1"] = dv1;
    result["dv2"] = dv2;
    result["total_dv"] = dv1 + dv2;
    result["transfer_time_s"] = PI * std::sqrt(a_transfer * a_transfer * a_transfer / mu);
    return result;
}

py::dict planet_ecliptic_position(
    double L0_deg, double period_yr, double a_au, double t_centuries)
{
    double years = t_centuries * 100.0;
    double L_deg = std::fmod(L0_deg + 360.0 / period_yr * years, 360.0);
    if (L_deg < 0) L_deg += 360.0;
    double L = deg_to_rad(L_deg);
    double x = a_au * std::cos(L);
    double y = a_au * std::sin(L);
    double lon = std::fmod(rad_to_deg(std::atan2(y, x)), 360.0);
    if (lon < 0) lon += 360.0;
    py::dict result;
    result["x_au"] = x;
    result["y_au"] = y;
    result["z_au"] = 0.0;
    result["lon_deg"] = lon;
    result["lat_deg"] = 0.0;
    result["r_au"] = a_au;
    return result;
}

std::tuple<double, double, double> position_from_elements(
    double a, double e, double i_deg, double raan_deg, double argp_deg, double nu_deg,
    double jd, double mu, double epoch_jd)
{
    double n = std::sqrt(mu / (a * a * a));
    double dt = (jd - epoch_jd) * 86400.0;
    double M0 = mean_anomaly_from_true(nu_deg, e);
    double M = deg_to_rad(M0) + n * dt;
    double nu = true_anomaly_from_mean(rad_to_deg(M), e, 1e-8);
    double r = a * (1.0 - e * e) / (1.0 + e * std::cos(deg_to_rad(nu)));
    double i = deg_to_rad(i_deg);
    double raan = deg_to_rad(raan_deg);
    double argp = deg_to_rad(argp_deg);
    double nu_r = deg_to_rad(nu);
    double x_orb = r * std::cos(nu_r);
    double y_orb = r * std::sin(nu_r);
    double cos_raan = std::cos(raan), sin_raan = std::sin(raan);
    double cos_i = std::cos(i), sin_i = std::sin(i);
    double cos_argp = std::cos(argp), sin_argp = std::sin(argp);
    double x = (cos_raan * cos_argp - sin_raan * sin_argp * cos_i) * x_orb
        + (-cos_raan * sin_argp - sin_raan * cos_argp * cos_i) * y_orb;
    double y = (sin_raan * cos_argp + cos_raan * sin_argp * cos_i) * x_orb
        + (-sin_raan * sin_argp + cos_raan * cos_argp * cos_i) * y_orb;
    double z = sin_argp * sin_i * x_orb + cos_argp * sin_i * y_orb;
    return {x, y, z};
}

double redshift_from_velocity(double v_kms) {
    double beta = v_kms / (C_M_S / 1000.0);
    if (std::abs(beta) >= 1.0) return INF;
    return std::sqrt((1.0 + beta) / (1.0 - beta)) - 1.0;
}

double hubble_flow_velocity(double distance_mpc, double H0) {
    return H0 * distance_mpc;
}

double angular_diameter_distance_mpc(
    double z, double H0, double Om0, double Ode0, int steps)
{
    double d_l = luminosity_distance_mpc(z, H0, Om0, Ode0, steps);
    return d_l / ((1.0 + z) * (1.0 + z));
}

double absolute_magnitude(double apparent_m, double distance_pc) {
    return apparent_m - distance_modulus(distance_pc);
}

double apparent_magnitude(double absolute_m, double distance_pc) {
    return absolute_m + distance_modulus(distance_pc);
}

py::array_t<double> angular_separation_from_target_batch(
    double ra0_hours, double dec0_deg,
    py::array_t<double> ra_hours, py::array_t<double> dec_deg)
{
    py::buffer_info bra = ra_hours.request(), bdec = dec_deg.request();
    if (bra.ndim != 1 || bdec.ndim != 1 || bra.shape[0] != bdec.shape[0]) {
        throw std::runtime_error("angular_separation_from_target_batch: 1D arrays of equal length required");
    }
    size_t n = bra.shape[0];
    const double* pra = static_cast<const double*>(bra.ptr);
    const double* pdec = static_cast<const double*>(bdec.ptr);
    auto out = py::array_t<double>(n);
    double* pout = static_cast<double*>(out.request().ptr);
    for (size_t i = 0; i < n; ++i) {
        pout[i] = angular_separation_deg(ra0_hours, dec0_deg, pra[i], pdec[i]);
    }
    return out;
}

PYBIND11_MODULE(_pytekt_universe, m) {
    m.doc() = "Fast astronomy kernels for pytekt.universe";
    m.def("gmst_hours", &gmst_hours, py::arg("jd"), "Greenwich Mean Sidereal Time (hours).");
    m.def("equatorial_to_horizontal", &equatorial_to_horizontal,
          py::arg("ra_hours"), py::arg("dec_deg"),
          py::arg("latitude_deg"), py::arg("longitude_deg"), py::arg("jd"),
          "Return (altitude_deg, azimuth_deg).");
    m.def("equatorial_to_horizontal_batch", &equatorial_to_horizontal_batch,
          py::arg("ra_hours"), py::arg("dec_deg"),
          py::arg("latitude_deg"), py::arg("longitude_deg"), py::arg("jd"),
          "Batch Alt/Az for 1D arrays; returns (alt, az).");
    m.def("angular_separation_deg", &angular_separation_deg,
          py::arg("ra1_hours"), py::arg("dec1_deg"),
          py::arg("ra2_hours"), py::arg("dec2_deg"),
          "Great-circle separation in degrees.");
    m.def("equatorial_to_galactic", &equatorial_to_galactic,
          py::arg("ra_hours"), py::arg("dec_deg"),
          "Return (galactic_l_deg, galactic_b_deg).");
    m.def("moon_phase_fraction", &moon_phase_fraction, py::arg("jd"),
          "Moon phase fraction 0..1.");
    m.def("comoving_distance_mpc", &comoving_distance_mpc,
          py::arg("z"), py::arg("H0"), py::arg("Om0"), py::arg("Ode0"),
          py::arg("steps") = 200,
          "Comoving distance Mpc (flat LCDM).");
    m.def("luminosity_distance_mpc", &luminosity_distance_mpc,
          py::arg("z"), py::arg("H0"), py::arg("Om0"), py::arg("Ode0"),
          py::arg("steps") = 200,
          "Luminosity distance Mpc.");
    m.def("lookback_time_gyr", &lookback_time_gyr,
          py::arg("z"), py::arg("H0"), py::arg("Om0"), py::arg("Ode0"),
          py::arg("steps") = 200,
          "Lookback time Gyr.");
    m.def("flux_to_magnitude", &flux_to_magnitude,
          py::arg("flux"), py::arg("flux_zero") = 1.0);
    m.def("magnitude_to_flux", &magnitude_to_flux,
          py::arg("magnitude"), py::arg("flux_zero") = 1.0);
    m.def("distance_modulus", &distance_modulus, py::arg("distance_pc"));
    m.def("horizontal_to_equatorial", &horizontal_to_equatorial,
          py::arg("altitude_deg"), py::arg("azimuth_deg"),
          py::arg("latitude_deg"), py::arg("longitude_deg"), py::arg("jd"),
          "Return (ra_hours, dec_deg).");
    m.def("lst_hours", &lst_hours,
          py::arg("jd"), py::arg("longitude_deg"),
          "Local sidereal time in hours.");
    m.def("ecliptic_to_equatorial", &ecliptic_to_equatorial,
          py::arg("lon_deg"), py::arg("lat_deg") = 0.0,
          "Return (ra_hours, dec_deg).");
    m.def("ecliptic_to_equatorial_batch", &ecliptic_to_equatorial_batch,
          py::arg("lon_deg"), py::arg("lat_deg"),
          "Batch ecliptic to equatorial; returns (ra_hours, dec_deg).");
    m.def("precess", &precess,
          py::arg("ra_hours"), py::arg("dec_deg"),
          py::arg("from_epoch") = 2000.0, py::arg("to_epoch") = 2000.0,
          "Simplified precession; returns (ra_hours, dec_deg).");
    m.def("air_mass", &air_mass,
          py::arg("altitude_deg"), py::arg("pickering") = false);
    m.def("air_mass_batch", &air_mass_batch,
          py::arg("altitude_deg"), py::arg("pickering") = false);
    m.def("is_circumpolar", &is_circumpolar,
          py::arg("dec_deg"), py::arg("latitude_deg"));
    m.def("rise_set_approx", &rise_set_approx,
          py::arg("ra_hours"), py::arg("dec_deg"),
          py::arg("latitude_deg"), py::arg("longitude_deg"), py::arg("jd"),
          "Approximate rise/transit/set Julian dates.");
    m.def("moon_illumination", &moon_illumination, py::arg("jd"));
    m.def("true_anomaly_from_mean", &true_anomaly_from_mean,
          py::arg("mean_anomaly_deg"), py::arg("eccentricity"),
          py::arg("tol") = 1e-8);
    m.def("mean_anomaly_from_true", &mean_anomaly_from_true,
          py::arg("true_anomaly_deg"), py::arg("eccentricity"));
    m.def("kepler_third_law", &kepler_third_law,
          py::arg("semi_major_axis"), py::arg("mu"));
    m.def("hohmann_transfer", &hohmann_transfer,
          py::arg("r1"), py::arg("r2"), py::arg("mu"));
    m.def("planet_ecliptic_position", &planet_ecliptic_position,
          py::arg("L0_deg"), py::arg("period_yr"), py::arg("a_au"),
          py::arg("t_centuries"));
    m.def("position_from_elements", &position_from_elements,
          py::arg("a"), py::arg("e"), py::arg("i_deg"), py::arg("raan_deg"),
          py::arg("argp_deg"), py::arg("nu_deg"), py::arg("jd"), py::arg("mu"),
          py::arg("epoch_jd") = J2000,
          "Return (x, y, z) in same units as a.");
    m.def("redshift_from_velocity", &redshift_from_velocity, py::arg("v_kms"));
    m.def("hubble_flow_velocity", &hubble_flow_velocity,
          py::arg("distance_mpc"), py::arg("H0"));
    m.def("angular_diameter_distance_mpc", &angular_diameter_distance_mpc,
          py::arg("z"), py::arg("H0"), py::arg("Om0"), py::arg("Ode0"),
          py::arg("steps") = 200);
    m.def("absolute_magnitude", &absolute_magnitude,
          py::arg("apparent_m"), py::arg("distance_pc"));
    m.def("apparent_magnitude", &apparent_magnitude,
          py::arg("absolute_m"), py::arg("distance_pc"));
    m.def("angular_separation_from_target_batch", &angular_separation_from_target_batch,
          py::arg("ra0_hours"), py::arg("dec0_deg"),
          py::arg("ra_hours"), py::arg("dec_deg"),
          "Separation in degrees from one target to many.");
}
