/*
 * toon shader (0.4.2)
 * author: gnya
 */

#define GET_SHADOW(id)          ((id >> 0) & 63)
#define GET_TRANSPARENT(id)     ((id >> 6) & 63)
#define GET_SHADOW_PROPS(id)    ((id >> 12) & 7)

/*
 * Get this shadow group id and shadow props.
 */
void get_this_shadow_group(output int group, output int props) {
    float obj_id_f, mat_id_f;
    getattribute("object:index", obj_id_f);
    getattribute("material:index", mat_id_f);

    int obj_id = (int) obj_id_f;
    int mat_id = (int) mat_id_f;
    group = GET_SHADOW(obj_id) ? GET_SHADOW(obj_id) : GET_SHADOW(mat_id);
    props = GET_SHADOW_PROPS(obj_id) ? GET_SHADOW_PROPS(obj_id) : GET_SHADOW_PROPS(mat_id);
}

/*
 * Get hit shadow group id and shadow props.
 */
void get_hit_shadow_group(output int group, output int props) {
    float obj_id_f, mat_id_f;
    getmessage("trace", "object:index", obj_id_f);
    getmessage("trace", "material:index", mat_id_f);

    int obj_id = (int) obj_id_f;
    int mat_id = (int) mat_id_f;
    group = GET_SHADOW(obj_id) ? GET_SHADOW(obj_id) : GET_SHADOW(mat_id);
    props = GET_SHADOW_PROPS(obj_id) ? GET_SHADOW_PROPS(obj_id) : GET_SHADOW_PROPS(mat_id);
}

/*
 * Get this transparent group id.
 */
void get_this_transparent_group(output int group) {
    float obj_id_f, mat_id_f;
    getattribute("object:index", obj_id_f);
    getattribute("material:index", mat_id_f);

    int obj_id = (int) obj_id_f;
    int mat_id = (int) mat_id_f;
    group = GET_TRANSPARENT(obj_id) ? GET_TRANSPARENT(obj_id) : GET_TRANSPARENT(mat_id);
}

/*
 * Get hit transparent group id.
 */
void get_hit_transparent_group(output int group) {
    float obj_id_f, mat_id_f;
    getmessage("trace", "object:index", obj_id_f);
    getmessage("trace", "material:index", mat_id_f);

    int obj_id = (int) obj_id_f;
    int mat_id = (int) mat_id_f;
    group = GET_TRANSPARENT(obj_id) ? GET_TRANSPARENT(obj_id) : GET_TRANSPARENT(mat_id);
}
