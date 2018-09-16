module TrashPage.View exposing (capsFirst, inputDay, inputVolume, inputZero, metricWord, noSaveButtonIcon, saveButton, saveButtonIcon, trashSentence, view, viewErrors, viewStats)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Svg
import Svg.Attributes as SvgAttr
import Svg.Events as SvgEvent
import Trash.Enum.Metric exposing (Metric(..))
import TrashPage.Model exposing (..)
import TrashPage.Update exposing (..)


saveButtonIcon : String
saveButtonIcon =
    "/static/trashinator/checkmark.svg"


noSaveButtonIcon : String
noSaveButtonIcon =
    "/static/trashinator/checkmark-faded.svg"


view : Model -> Html Msg
view model =
    div []
        [ trashSentence model.opts model.entry
        , inputDay model.opts
        , inputZero model.opts
        , saveButton model.meta model.entry
        , inputVolume model.entry
        , viewStats model.entry.metric model.stats
        , viewErrors model.meta
        ]


trashSentence : TPOptions -> TPEntry -> Html Msg
trashSentence options entry =
    let
        howMuch =
            case entry.volume of
                Nothing ->
                    "..."

                Just 0 ->
                    "nothing"

                Just x ->
                    toString x ++ " " ++ metricWord x entry.metric ++ "  of trash"

        when =
            capsFirst <| whichDayToString options.day
    in
    p
        [ id "trashSentence" ]
        [ text <| when ++ " I took out " ++ howMuch ++ "." ]


inputZero : TPOptions -> Html Msg
inputZero opts =
    p [ id "inputZero", onClick SaveZero ]
        [ text <| "Nothing " ++ whichDayToString opts.day ]


inputVolume : TPEntry -> Html Msg
inputVolume entry =
    p [ id "inputVolume" ]
        [ input [ placeholder "How many?", onInput ChangeVolume ] []
        , text <| " " ++ metricWord 0 entry.metric ++ " of trash"
        ]


inputDay : TPOptions -> Html Msg
inputDay opts =
    p [ id "inputDay" ] <|
        List.map
            (\d ->
                span
                    (if opts.day == d then
                        [ class "selected" ]

                     else
                        [ onClick <| ChangeDay d ]
                    )
                    [ text <| " " ++ whichDayToString d ]
            )
            [ Today, Yesterday, TwoDaysAgo ]


saveButton : TPMeta -> TPEntry -> Html Msg
saveButton meta entry =
    if meta.changed && meta.error == Nothing && entry.volume /= Nothing then
        img
            [ onClick Save
            , id "saveButton"
            , src saveButtonIcon
            , alt "save"
            ]
            []

    else
        img [ id "saveButton", src noSaveButtonIcon, alt "can't save" ] []


viewStats : Metric -> TPStats -> Html Msg
viewStats metric stats =
    let
        userRatio =
            stats.userPerPersonPerWeek
                / (stats.sitePerPersonPerWeek * 2)

        ratioWidth =
            toString (Basics.min (userRatio * 30) 30) ++ "ex"
    in
    div [ class "stats" ]
        [ Svg.svg
            [ SvgAttr.id "statsImage", SvgAttr.width "32ex", SvgAttr.height "3em" ]
            -- Stats bar outline
            [ Svg.rect
                [ SvgAttr.fill "#e3dbdb"
                , SvgAttr.width "30ex"
                , SvgAttr.height "2em"
                , SvgAttr.x "1ex"
                , SvgAttr.y ".5em"
                , SvgAttr.rx "3pt"
                , SvgAttr.ry "3pt"
                ]
                []

            -- Stats bar filled area color
            , Svg.rect
                [ SvgAttr.fill "#6c6753"
                , SvgAttr.stroke "none"
                , SvgAttr.width ratioWidth
                , SvgAttr.height "2em"
                , SvgAttr.x "1ex"
                , SvgAttr.y ".5em"
                , SvgAttr.rx "3pt"
                , SvgAttr.ry "3pt"
                ]
                []

            -- Stats bar midpoint marker
            , Svg.rect
                [ SvgAttr.fill "#5aa02c"
                , SvgAttr.stroke "none"
                , SvgAttr.width "1ex"
                , SvgAttr.height "2em"
                , SvgAttr.x "16ex"
                , SvgAttr.y ".5em"
                ]
                []

            -- Stats bar border outline
            , Svg.rect
                [ SvgAttr.fill "none"
                , SvgAttr.stroke "#aca793"
                , SvgAttr.strokeWidth "3pt"
                , SvgAttr.width "30ex"
                , SvgAttr.height "2em"
                , SvgAttr.x "1ex"
                , SvgAttr.y ".5em"
                , SvgAttr.rx "3pt"
                , SvgAttr.ry "3pt"
                ]
                []
            ]
        , div []
            [ p []
                [ text <|
                    "Your average: "
                        ++ toString stats.userPerPersonPerWeek
                        ++ " "
                        ++ metricWord stats.userPerPersonPerWeek metric
                        ++ " per person per week"
                ]
            , p
                []
                [ text <|
                    "Site average: "
                        ++ toString stats.sitePerPersonPerWeek
                        ++ " "
                        ++ metricWord stats.sitePerPersonPerWeek metric
                        ++ " per person per week"
                ]
            ]
        ]


viewErrors : TPMeta -> Html Msg
viewErrors meta =
    case meta.error of
        Nothing ->
            text ""

        Just msg ->
            p [ class "error" ] [ text <| "(" ++ msg ++ ")" ]



-- Helpers


metricWord : Float -> Metric -> String
metricWord vol metric =
    let
        plural =
            metric |> toString |> String.toLower

        singular =
            String.dropRight 1 plural
    in
    if vol == 1.0 then
        singular

    else
        plural


capsFirst : String -> String
capsFirst s =
    let
        start =
            String.toUpper <| String.left 1 s

        end =
            String.dropLeft 1 s
    in
    start ++ end
