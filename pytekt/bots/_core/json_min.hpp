#ifndef PYTEKT_BOTS_JSON_MIN_HPP
#define PYTEKT_BOTS_JSON_MIN_HPP

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <sstream>
#include <cctype>
#include <stdexcept>
#include <algorithm>

namespace pytekt {
namespace bots {

enum class JsonType {
    Null,
    Boolean,
    Number,
    String,
    Array,
    Object
};

struct JsonValue;

using JsonObject = std::map<std::string, JsonValue>;
using JsonArray = std::vector<JsonValue>;

struct JsonValue {
    JsonType type = JsonType::Null;
    bool bool_val = false;
    double num_val = 0.0;
    std::string str_val;
    JsonArray arr_val;
    JsonObject obj_val;

    static JsonValue null_val() {
        return JsonValue();
    }

    static JsonValue from_bool(bool b) {
        JsonValue v;
        v.type = JsonType::Boolean;
        v.bool_val = b;
        return v;
    }

    static JsonValue from_number(double n) {
        JsonValue v;
        v.type = JsonType::Number;
        v.num_val = n;
        return v;
    }

    static JsonValue from_string(const std::string& s) {
        JsonValue v;
        v.type = JsonType::String;
        v.str_val = s;
        return v;
    }

    bool is_null() const { return type == JsonType::Null; }
    bool is_bool() const { return type == JsonType::Boolean; }
    bool is_number() const { return type == JsonType::Number; }
    bool is_string() const { return type == JsonType::String; }
    bool is_array() const { return type == JsonType::Array; }
    bool is_object() const { return type == JsonType::Object; }

    bool contains(const std::string& key) const {
        if (!is_object()) return false;
        return obj_val.find(key) != obj_val.end();
    }

    const JsonValue& get(const std::string& key) const {
        static const JsonValue null_inst;
        if (!is_object()) return null_inst;
        auto it = obj_val.find(key);
        if (it != obj_val.end()) return it->second;
        return null_inst;
    }

    std::string get_string(const std::string& key, const std::string& default_val = "") const {
        const auto& v = get(key);
        if (v.is_string()) return v.str_val;
        if (v.is_number()) {
            std::ostringstream ss;
            ss << v.num_val;
            return ss.str();
        }
        return default_val;
    }

    double get_number(const std::string& key, double default_val = 0.0) const {
        const auto& v = get(key);
        if (v.is_number()) return v.num_val;
        return default_val;
    }

    int64_t get_int64(const std::string& key, int64_t default_val = 0) const {
        const auto& v = get(key);
        if (v.is_number()) return static_cast<int64_t>(v.num_val);
        if (v.is_string()) {
            try {
                return std::stoll(v.str_val);
            } catch (...) {
                return default_val;
            }
        }
        return default_val;
    }

    bool get_bool(const std::string& key, bool default_val = false) const {
        const auto& v = get(key);
        if (v.is_bool()) return v.bool_val;
        return default_val;
    }

    std::string serialize() const {
        std::ostringstream ss;
        serialize_into(ss);
        return ss.str();
    }

    void serialize_into(std::ostringstream& ss) const {
        switch (type) {
            case JsonType::Null:
                ss << "null";
                break;
            case JsonType::Boolean:
                ss << (bool_val ? "true" : "false");
                break;
            case JsonType::Number:
                if (num_val == static_cast<int64_t>(num_val)) {
                    ss << static_cast<int64_t>(num_val);
                } else {
                    ss << num_val;
                }
                break;
            case JsonType::String:
                ss << '"';
                for (char c : str_val) {
                    if (c == '"') ss << "\\\"";
                    else if (c == '\\') ss << "\\\\";
                    else if (c == '\b') ss << "\\b";
                    else if (c == '\f') ss << "\\f";
                    else if (c == '\n') ss << "\\n";
                    else if (c == '\r') ss << "\\r";
                    else if (c == '\t') ss << "\\t";
                    else ss << c;
                }
                ss << '"';
                break;
            case JsonType::Array:
                ss << '[';
                for (size_t i = 0; i < arr_val.size(); ++i) {
                    if (i > 0) ss << ",";
                    arr_val[i].serialize_into(ss);
                }
                ss << ']';
                break;
            case JsonType::Object:
                ss << '{';
                bool first = true;
                for (const auto& kv : obj_val) {
                    if (!first) ss << ",";
                    first = false;
                    ss << '"' << kv.first << "\":";
                    kv.second.serialize_into(ss);
                }
                ss << '}';
                break;
        }
    }
};

class JsonParser {
public:
    static JsonValue parse(const std::string& str) {
        size_t idx = 0;
        skip_ws(str, idx);
        if (idx >= str.size()) {
            return JsonValue::null_val();
        }
        return parse_value(str, idx);
    }

private:
    static void skip_ws(const std::string& s, size_t& idx) {
        while (idx < s.size() && (std::isspace(static_cast<unsigned char>(s[idx])) || s[idx] == '\0')) {
            idx++;
        }
    }

    static JsonValue parse_value(const std::string& s, size_t& idx) {
        skip_ws(s, idx);
        if (idx >= s.size()) return JsonValue::null_val();

        char c = s[idx];
        if (c == '{') return parse_object(s, idx);
        if (c == '[') return parse_array(s, idx);
        if (c == '"') return parse_string(s, idx);
        if (c == 't' || c == 'f') return parse_bool(s, idx);
        if (c == 'n') return parse_null(s, idx);
        if (c == '-' || std::isdigit(static_cast<unsigned char>(c))) return parse_number(s, idx);

        return JsonValue::null_val();
    }

    static JsonValue parse_object(const std::string& s, size_t& idx) {
        JsonValue val;
        val.type = JsonType::Object;
        idx++; // skip '{'

        while (idx < s.size()) {
            skip_ws(s, idx);
            if (idx >= s.size()) break;
            if (s[idx] == '}') {
                idx++;
                return val;
            }

            JsonValue key = parse_string(s, idx);
            skip_ws(s, idx);
            if (idx < s.size() && s[idx] == ':') {
                idx++;
            }
            JsonValue child = parse_value(s, idx);
            val.obj_val[key.str_val] = child;

            skip_ws(s, idx);
            if (idx < s.size() && s[idx] == ',') {
                idx++;
            } else if (idx < s.size() && s[idx] == '}') {
                idx++;
                return val;
            }
        }
        return val;
    }

    static JsonValue parse_array(const std::string& s, size_t& idx) {
        JsonValue val;
        val.type = JsonType::Array;
        idx++; // skip '['

        while (idx < s.size()) {
            skip_ws(s, idx);
            if (idx >= s.size()) break;
            if (s[idx] == ']') {
                idx++;
                return val;
            }

            JsonValue child = parse_value(s, idx);
            val.arr_val.push_back(child);

            skip_ws(s, idx);
            if (idx < s.size() && s[idx] == ',') {
                idx++;
            } else if (idx < s.size() && s[idx] == ']') {
                idx++;
                return val;
            }
        }
        return val;
    }

    static JsonValue parse_string(const std::string& s, size_t& idx) {
        JsonValue val;
        val.type = JsonType::String;
        if (idx >= s.size() || s[idx] != '"') return val;
        idx++; // skip opening '"'

        std::string res;
        while (idx < s.size()) {
            char c = s[idx++];
            if (c == '"') {
                val.str_val = res;
                return val;
            }
            if (c == '\\' && idx < s.size()) {
                char esc = s[idx++];
                if (esc == '"') res.push_back('"');
                else if (esc == '\\') res.push_back('\\');
                else if (esc == '/') res.push_back('/');
                else if (esc == 'b') res.push_back('\b');
                else if (esc == 'f') res.push_back('\f');
                else if (esc == 'n') res.push_back('\n');
                else if (esc == 'r') res.push_back('\r');
                else if (esc == 't') res.push_back('\t');
                else if (esc == 'u' && idx + 4 <= s.size()) {
                    idx += 4;
                    res.push_back('?');
                } else {
                    res.push_back(esc);
                }
            } else {
                res.push_back(c);
            }
        }
        val.str_val = res;
        return val;
    }

    static JsonValue parse_bool(const std::string& s, size_t& idx) {
        if (s.compare(idx, 4, "true") == 0) {
            idx += 4;
            return JsonValue::from_bool(true);
        }
        if (s.compare(idx, 5, "false") == 0) {
            idx += 5;
            return JsonValue::from_bool(false);
        }
        return JsonValue::null_val();
    }

    static JsonValue parse_null(const std::string& s, size_t& idx) {
        if (s.compare(idx, 4, "null") == 0) {
            idx += 4;
        }
        return JsonValue::null_val();
    }

    static JsonValue parse_number(const std::string& s, size_t& idx) {
        size_t start = idx;
        if (s[idx] == '-') idx++;
        while (idx < s.size() && (std::isdigit(static_cast<unsigned char>(s[idx])) || s[idx] == '.' || s[idx] == 'e' || s[idx] == 'E' || s[idx] == '+' || s[idx] == '-')) {
            idx++;
        }
        std::string num_str = s.substr(start, idx - start);
        try {
            double d = std::stod(num_str);
            return JsonValue::from_number(d);
        } catch (...) {
            return JsonValue::from_number(0.0);
        }
    }
};

} // namespace bots
} // namespace pytekt

#endif // PYTEKT_BOTS_JSON_MIN_HPP
