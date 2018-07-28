module UpdateTrashPage exposing (..)
import Models exposing (..)

type Msg = ChangeAmount String

updateTrashPage : Msg -> TrashPage -> (TrashPage, Cmd Msg)
updateTrashPage msg model = case msg of
    (ChangeAmount txt) -> ( changeAmount txt model, Cmd.none )

changeAmount : String -> TrashPage -> TrashPage
changeAmount txt page = case String.toFloat txt of
    (Err _) -> { page | error = Just "Amount must be a number" }
    (Ok x) ->
        if x < 0 then { page | error = Just "Amount must be 0 or more" }
        else { page | error = Nothing
                    , trash = Just <| setAmount x
                                   <| Maybe.withDefault emptyTrash page.trash
             } 

setAmount : Float -> Trash -> Trash
setAmount x trash = case trash.amount of
    (Litres _) -> { trash | amount = Litres x }
    (Gallons _) -> { trash | amount = Gallons x }
